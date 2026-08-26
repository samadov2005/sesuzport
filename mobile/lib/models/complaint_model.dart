class ComplaintModel {
  final int id;
  final String ticketId;
  final String description;
  final String status;
  final String statusDisplay;
  final String moderationComment;
  final double latitude;
  final double longitude;
  final String createdAt;
  final String? resolvedAt;

  ComplaintModel({
    required this.id,
    required this.ticketId,
    required this.description,
    required this.status,
    required this.statusDisplay,
    required this.moderationComment,
    required this.latitude,
    required this.longitude,
    required this.createdAt,
    this.resolvedAt,
  });

  factory ComplaintModel.fromJson(Map<String, dynamic> json) {
    return ComplaintModel(
      id: json['id'] ?? 0,
      ticketId: json['ticket_id'] ?? '',
      description: json['description'] ?? '',
      status: json['status'] ?? 'PENDING',
      statusDisplay: json['status_display'] ?? 'Kutilmoqda',
      moderationComment: json['moderation_comment'] ?? '',
      latitude: (json['latitude'] as num?)?.toDouble() ?? 0.0,
      longitude: (json['longitude'] as num?)?.toDouble() ?? 0.0,
      createdAt: json['created_at'] ?? '',
      resolvedAt: json['resolved_at'],
    );
  }
}
