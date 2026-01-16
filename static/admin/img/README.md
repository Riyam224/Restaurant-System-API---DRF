# Admin Branding Assets

Place your custom admin panel branding assets in this directory.

## Required Files

### Logo
- **Filename**: `logo.png` or `logo.svg`
- **Recommended size**: 200x60px (or similar aspect ratio)
- **Format**: PNG with transparency or SVG
- **Usage**: Displayed in the top-left of the admin panel

### Favicon
- **Filename**: `favicon.ico`
- **Recommended size**: 32x32px or 16x16px
- **Format**: ICO format
- **Usage**: Browser tab icon

### Login Page Logo (Optional)
- **Filename**: `login-logo.png`
- **Recommended size**: 300x100px
- **Format**: PNG with transparency
- **Usage**: Displayed on the admin login page

## How to Add Your Logo

1. Add your logo file to this directory
2. Update the Jazzmin settings in `config/settings.py`:
   ```python
   JAZZMIN_SETTINGS = {
       ...
       "site_logo": "admin/img/logo.png",
       "site_icon": "admin/img/favicon.ico",
       "login_logo": "admin/img/login-logo.png",
       ...
   }
   ```
3. Run `python manage.py collectstatic` to collect the new assets
4. Refresh your admin panel

## Example Logo Design Guidelines

- Use your restaurant's brand colors
- Keep it simple and recognizable
- Ensure good contrast for readability
- Test on both light and dark backgrounds
- Make it mobile-responsive friendly
