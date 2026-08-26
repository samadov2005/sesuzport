class StoreModel {
  final int id;
  final String name;
  final String address;
  final double? latitude;
  final double? longitude;
  final String phone;
  final double rating;
  final String safetyStatus;
  final String safetyStatusDisplay;
  final double? distanceKm;

  StoreModel({
    required this.id,
    required this.name,
    required this.address,
    this.latitude,
    this.longitude,
    required this.phone,
    required this.rating,
    required this.safetyStatus,
    required this.safetyStatusDisplay,
    this.distanceKm,
  });

  factory StoreModel.fromJson(Map<String, dynamic> json) {
    return StoreModel(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      address: json['address'] ?? '',
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      phone: json['phone'] ?? '',
      rating: (json['rating'] as num?)?.toDouble() ?? 0.0,
      safetyStatus: json['safety_status'] ?? 'GREEN',
      safetyStatusDisplay: json['safety_status_display'] ?? 'Xavfsiz',
      distanceKm: (json['distance_km'] as num?)?.toDouble(),
    );
  }
}
