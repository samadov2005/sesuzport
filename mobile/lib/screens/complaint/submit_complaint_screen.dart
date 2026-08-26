import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import '../../constants/app_colors.dart';
import '../../services/api_service.dart';

class SubmitComplaintScreen extends StatefulWidget {
  final Uint8List photoBytes;
  final String photoBase64;

  const SubmitComplaintScreen({
    super.key,
    required this.photoBytes,
    required this.photoBase64,
  });

  @override
  State<SubmitComplaintScreen> createState() => _SubmitComplaintScreenState();
}

class _SubmitComplaintScreenState extends State<SubmitComplaintScreen> {
  final _descController = TextEditingController();
  String _selectedCategory = "Muddati o'tgan mahsulot";
  double? _latitude;
  double? _longitude;
  bool _isGettingLocation = false;
  bool _isSubmitting = false;
  String? _errorMessage;

  final List<String> _categories = [
    "Muddati o'tgan mahsulot",
    "Sanitariya va gigiyena buzilishi",
    "Chek berilmasligi / Narx oshirilishi",
    "Sifatsiz yoki buzilgan tovar",
    "Boshqa qoidabuzarlik",
  ];

  @override
  void initState() {
    super.initState();
    _determinePosition();
  }

  Future<void> _determinePosition() async {
    setState(() => _isGettingLocation = true);
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        _latitude = 41.311081;
        _longitude = 69.240562;
        setState(() => _isGettingLocation = false);
        return;
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }

      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: const Duration(seconds: 5),
      );
      _latitude = position.latitude;
      _longitude = position.longitude;
    } catch (_) {
      _latitude = 41.311081;
      _longitude = 69.240562;
    } finally {
      if (mounted) setState(() => _isGettingLocation = false);
    }
  }

  Future<void> _submit() async {
    final customDesc = _descController.text.trim();
    final fullDescription = customDesc.isNotEmpty
        ? "$_selectedCategory: $customDesc"
        : _selectedCategory;

    if (_latitude == null || _longitude == null) {
      setState(() => _errorMessage = "GPS lokatsiya aniqlanmadi. Iltimos, lokatsiyani yoqing.");
      return;
    }

    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
    });

    final result = await ApiService.submitComplaint(
      description: fullDescription,
      imageBase64: widget.photoBase64,
      latitude: _latitude!,
      longitude: _longitude!,
    );

    setState(() => _isSubmitting = false);

    if (result['success'] == true) {
      if (!mounted) return;
      _showSuccessDialog(result['ticket_id']);
    } else {
      setState(() => _errorMessage = result['error'] ?? "Xatolik yuz berdi.");
    }
  }

  void _showSuccessDialog(String ticketId) {
    final c = context.colors;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        backgroundColor: c.surface,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.safeGreen.withOpacity(0.15),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.check_circle_rounded, color: AppColors.safeGreen, size: 50),
            ),
            const SizedBox(height: 16),
            Text(
              'Murojaat qabul qilindi!',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: c.textPrimary),
            ),
            const SizedBox(height: 8),
            Text(
              'Chipta raqami: $ticketId',
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.primaryLight),
            ),
            const SizedBox(height: 12),
            Text(
              'Murojaatingiz darhol SES inspektorlari nazoratiga olindi va tez orada ko\'rib chiqiladi.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 12, color: c.textSecondary),
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 46,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.of(ctx).pop();
                  Navigator.of(context).pop();
                  Navigator.of(context).pop();
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: const Text('Tushunarli', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _descController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final c = context.colors;

    return Scaffold(
      backgroundColor: c.background,
      appBar: AppBar(
        backgroundColor: c.surface,
        elevation: 0,
        title: Text(
          'Murojaatni tasdiqlash',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: c.textPrimary),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Captured Photo Preview
            Container(
              height: 200,
              width: double.infinity,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.primaryLight.withOpacity(0.5)),
                image: DecorationImage(
                  image: MemoryImage(widget.photoBytes),
                  fit: BoxFit.cover,
                ),
              ),
              child: Stack(
                children: [
                  Positioned(
                    bottom: 12,
                    left: 12,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.black87,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        children: const [
                          Icon(Icons.verified, color: AppColors.safeGreen, size: 14),
                          SizedBox(width: 6),
                          Text(
                            'Jonli Kamera Dalili',
                            style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Location Box
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: c.surface,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: c.surfaceLight),
                boxShadow: c.cardShadow,
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppColors.primary.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(Icons.location_on, color: AppColors.primaryLight, size: 22),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Hodisa joylashuvi (GPS)',
                          style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: c.textPrimary),
                        ),
                        const SizedBox(height: 2),
                        _isGettingLocation
                            ? Text('GPS aniqlanmoqda...', style: TextStyle(fontSize: 11, color: c.textMuted))
                            : Text(
                                '${_latitude?.toStringAsFixed(5)}, ${_longitude?.toStringAsFixed(5)}',
                                style: TextStyle(fontSize: 11, color: c.textSecondary),
                              ),
                      ],
                    ),
                  ),
                  IconButton(
                    onPressed: _determinePosition,
                    icon: const Icon(Icons.refresh, color: AppColors.primaryLight, size: 20),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Category Selector
            Text(
              'Muammo toifasi:',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: c.textPrimary),
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _categories.map((cat) {
                final isSelected = _selectedCategory == cat;
                return ChoiceChip(
                  label: Text(cat),
                  selected: isSelected,
                  onSelected: (selected) {
                    if (selected) setState(() => _selectedCategory = cat);
                  },
                  selectedColor: AppColors.primary,
                  backgroundColor: c.surface,
                  labelStyle: TextStyle(
                    color: isSelected ? Colors.white : c.textSecondary,
                    fontSize: 12,
                    fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 20),

            // Description Input
            Text(
              'Qo\'shimcha izoh (ixtiyoriy):',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: c.textPrimary),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _descController,
              maxLines: 3,
              style: TextStyle(color: c.textPrimary),
              decoration: InputDecoration(
                hintText: 'Masalan: Mahsulot muddati 15 kunga o\'tib ketgan, peshtaxtada turibdi...',
                hintStyle: TextStyle(color: c.textMuted, fontSize: 13),
                filled: true,
                fillColor: c.surface,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: BorderSide(color: c.surfaceLight)),
                enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: BorderSide(color: c.surfaceLight)),
              ),
            ),
            const SizedBox(height: 16),

            // Error
            if (_errorMessage != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: Text(_errorMessage!, style: const TextStyle(color: AppColors.dangerRed, fontSize: 12)),
              ),

            // Submit Button
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: _isSubmitting ? null : _submit,
                style: ElevatedButton.styleFrom(
                  padding: EdgeInsets.zero,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
                child: Ink(
                  decoration: BoxDecoration(
                    gradient: AppColors.primaryGradient,
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: Center(
                    child: _isSubmitting
                        ? const SizedBox(
                            width: 22,
                            height: 22,
                            child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                          )
                        : const Text(
                            'Murojaatni yuborish',
                            style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white),
                          ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
