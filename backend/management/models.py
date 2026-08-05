from django.db import models
from solo.models import SingletonModel
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from PIL import Image
from osm_field.fields import OSMField, LatitudeField, LongitudeField
from colorfield.fields import ColorField # type: ignore
from phonenumber_field.modelfields import PhoneNumberField #type: ignore

class SocialMedia(models.Model):
    class Sites(models.TextChoices):
        INSTAGRAM = "IG", "Instagram"
        GITHUB = "GH", "GitHub"
        YOUTUBE = "YT", "YouTube"
        TIKTOK = "TT", "TikTok"
        DISCORD = "DC", "Discord"
        THREADS = "TR", "Threads"
        FACEBOOK = "FB", "Facebook" # doubt anyone uses this, it's old af
        TWITTER = "X", "Twitter/X" # i hate this name
        LINKEDIN = "LI", "LinkedIn" 
        WEBSITE = "WS", "Website"
        OTHER = "OT", "Other"
        # not adding reddit for obvious reasons

    # club = models.ForeignKey(Club, related_name='socialMedia', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    site = models.CharField(max_length=2, choices=Sites.choices, default=Sites.OTHER)

    def __str__(self):
        return self.site
    
    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"])
        ]

class Location(models.Model):
    location = OSMField(blank=True, help_text="Drag the pin to the location of your club's meeting place. You can also search for a location in the search bar.", null=True)
    location_lat = LatitudeField(null=True, blank=True)
    location_lon = LongitudeField(null=True, blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

class SiteSettings(SingletonModel):
    maintainance_mode = models.BooleanField(default=False)
    frontend_url = models.URLField(default="http://localhost:3000", max_length=100, help_text="The external url of frontend")
    school_name = models.CharField(default="SCHOOL", max_length=40, help_text="The name of the school *Use short form S.S (e.g, Richmond Green S.S)")
    council_name = models.CharField(default="STUCO", max_length=10, help_text="The name of the council (e.g, SAC)")
    school_email = models.EmailField(blank=True, max_length=50)
    school_phone = PhoneNumberField(blank=True)
    social_media = GenericRelation(SocialMedia)
    favicon = models.ImageField(default="management/default.png", upload_to="management/", help_text="This is the icon that appears in the browser tab. It should be a square image, preferably 32x32 pixels.")
    stuco_image = models.ImageField(default="management/default.png", upload_to="management/", help_text="This is the image for the club's logo. It should be a square image, preferably 300x300 pixels.")
    about_stuco = models.TextField(blank=True, max_length=500)
    about_school = models.TextField(blank=True, max_length=500)
    school_mascot = models.CharField(blank=True, max_length=50, help_text="This is the school's mascot. (e.g, Wildcat, Rattler) *Non-plural*.")
    school_primary_color = ColorField(default="#000000", help_text="This is the primary color of the school. It should be a hex code (e.g., #FF0000).")
    school_secondary_color = ColorField(default="#FFFFFF", help_text="This is the secondary color of the school. It should be a hex code (e.g., #000000).")
    school_tertiary_color = ColorField(default="#FF0000", help_text="This is the 'accent' color of the site. It should be a hex code (e.g., #FFFFFF).")
    # TODO: add website maintainers once users are done
    school_location = GenericRelation(Location)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.stuco_image and self.stuco_image.name != "management/default.png":
            img = Image.open(self.stuco_image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.stuco_image.path)

    def __str__(self):
        return "Site Configuration"

    class Meta: #BEN ISSUE: "Meta" overrides symbol of same name in class "SingletonModel"
        verbose_name = "Site Configuration"

class PageSettings(models.Model):
    class PageTypes(models.TextChoices):
        HOME = "HM", "Home"
        CLUBS = "CL", "Clubs"
        GALLERY = "GL", "Gallery"
        ABOUT = "AB", "About"

    internal_site_name = models.CharField(max_length=2, choices=PageTypes.choices)
    title = models.CharField(max_length=30, help_text="This is the title of the page. It is the TOP of the title section.")
    subtitle = models.CharField(blank=True, max_length=30, help_text="This is the subtitle of the page. It is the BOTTOM of the title section (secondary color). *NOT REQUIRED")
    tagline = models.TextField(blank=True, max_length=200, help_text="This is the bullet points of the title. It should be short and tells the user a bit about the page. *NOT REQUIRED")

    def __str__(self):
        return self.get_internal_site_name_display()
    
    class Meta:
        verbose_name = "Page Configuration"
