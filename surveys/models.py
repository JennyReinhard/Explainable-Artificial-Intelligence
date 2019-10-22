from django.db import models
from tinymce.models import HTMLField
from django.urls import reverse
from django.conf import settings

# Redirect constant
REDIRECTS = (
(0, 'Pre'),
(1, 'Intermediate'),
(2, 'Post')
)

# Survey model
class Survey(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='The surveys name',
        help_text="Give survey a name"
    )

    description = models.TextField(
        verbose_name='Short description of the survey',
        help_text='Give the survey a short description, so that others know what it us'
    )

    date_created = models.DateTimeField(auto_now=True)
    introduction = HTMLField(blank=True)
    ready = HTMLField(blank=True)
    ntrials = models.IntegerField(default=1, verbose_name='Trial multiplicator')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_DEFAULT, default=1)

    # Returns name in the admin panel
    def __str__(self):
        return self.name

    # Defines redirect url for generic views
    def get_absolute_url(self):
        return reverse('surveys:survey', kwargs={'pk':self.pk})

# Session model
class Session(models.Model):
    key = models.CharField(max_length=255, primary_key=True)

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        verbose_name='Related survey')

    start_date = models.DateTimeField(auto_now=True)
    end_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(
        protocol = 'both',
        unpack_ipv4=True
    )

    # Returns name in the admin panel
    def __str__(self):
        return str(self.key)

# Trial model
class Trial(models.Model):
    sessionkey = models.ForeignKey(Session, on_delete=models.CASCADE)
    reliability = models.IntegerField(null=True)
    dss = models.CharField(max_length=255, null=True)
    risk = models.CharField(max_length=255, null=True)
    scenario = models.CharField(max_length=255, null=True)
    package_value = models.IntegerField(null=True)
    attempts = models.IntegerField(null=True)
    errors = models.IntegerField(null=True)
    success = models.BooleanField(default=True)
    suggestion = models.CharField(max_length=255, null=True)
    best_choice = models.CharField(max_length=255, null=True)
    save_date = models.DateTimeField(auto_now=True, null=True)
    blockcounter = models.IntegerField(null=True)
    trialDuration = models.IntegerField(null=True)
    feedbackDuration = models.IntegerField(null=True)
    decision = models.CharField(max_length=255, null=True)
    defectiveness = models.BooleanField(default=False)
    profit = models.IntegerField(null=True)

    def __str__(self):
        return str(self.id)

#Redirect model
class Redirect(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    url = models.URLField(verbose_name='Redirect URL', max_length=255)
    purpose = models.IntegerField(verbose_name="Purpose", choices=REDIRECTS)

    # Returns name in the admin panel
    def __str__(self):
        return str(self.url)

# Model for a specific factor set
class SetFactor(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name="Factor name")
    blockfactor = models.BooleanField(verbose_name="Block factor")
    slug = models.SlugField(verbose_name='Factor slug')

    # Returns name in the admin panel
    def __str__(self):
        return str(self.name)

# Model for level of a factor set
class SetLevel(models.Model):
    set_factor = models.ForeignKey(SetFactor, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name="Factor Name")
    value = models.IntegerField(verbose_name="Factor value")
    slug = models.SlugField(verbose_name='Level slug')

    # Returns name in the admin panel
    def __str__(self):
        return str(self.name + ' [' + str(self.value) + ']')
