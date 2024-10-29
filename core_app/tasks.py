from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from core_app.models import FaceData
from core_app.enum.sub_system import SubSystems


@shared_task
def delete_old_facedata():
    now = timezone.now()
    subsystems = SubSystems.DEMO_HUB.value
    threshold_time = now - timedelta(hours=24)

    old_records = FaceData.objects.filter(
        created_at__lt=threshold_time,
        subsystem=subsystems
    )
    count, _ = old_records.delete()
    print(f'{count} FaceData records older than 24 hours were deleted.')