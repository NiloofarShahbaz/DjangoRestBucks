from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.core.mail import send_mail

from .models import Order


NOTIFICATION_EMAIL_TEMPLATE = "Dear {},\n\nYour order {} status has changed to {}."


@receiver(pre_save, sender=Order, dispatch_uid="send_email_on_status_change")
def send_email_on_status_change(sender, instance, *args, **kwargs):
    try:
        existing_sender = sender.objects.get(pk=instance.pk)
        if existing_sender.status != instance.status:
            # TODO: do this in a celery task
            send_mail(
                subject="Order status changed",
                message=NOTIFICATION_EMAIL_TEMPLATE.format(
                    instance.user.first_name or instance.user.username,
                    instance.pk,
                    instance.get_status_display(),
                ),
                from_email=None,
                recipient_list=(instance.user.email,),
                fail_silently=False,
            )
    except sender.DoesNotExist:
        pass
