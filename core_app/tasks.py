from datetime import timedelta
from django.utils import timezone
from core_app.models import FaceData
from core_app.enum.sub_system import SubSystems




def delete_old_facedata():
    # Get the current time
    now = timezone.now()
    
    # Get the subsystem
    subsystems = SubSystems.DEMO_HUB.value

    # Get all FaceData entries older than 24 hours
    threshold_time = now - timedelta(hours=24)

    # Filter and delete records older than 24 hours
    old_records = FaceData.objects.filter(
                        created_at__lt=threshold_time,
                        subsystem=subsystems)
    count, _ = old_records.delete()  # This deletes the records

    print(f'{count} FaceData records older than 24 hours were deleted.')