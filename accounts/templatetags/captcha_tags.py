# captcha_tags.py



from django import template
from captcha.fields import CaptchaField

register = template.Library()


@register.simple_tag
def captcha_form():
    return CaptchaField().widget.render('captcha', '', attrs={})

@register.simple_tag
def captcha_script():
    return CaptchaField().widget.render_js('captcha', '')

@register.simple_tag
def captcha_img():
    return CaptchaField().image()

@register.simple_tag
def captcha_audio():
    return CaptchaField().audio()
