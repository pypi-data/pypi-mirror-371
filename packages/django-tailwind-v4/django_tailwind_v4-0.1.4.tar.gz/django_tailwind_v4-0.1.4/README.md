# Django Tailwind CSS v4

[![PyPI version](https://img.shields.io/pypi/v/django-tailwind-v4.svg)](https://pypi.org/project/django-tailwind-v4/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple, beginner-friendly Django app to integrate Tailwind CSS v4 into your project.

This package automates the setup process by providing management commands to initialize your project with the necessary Tailwind configuration and install its dependencies, without requiring complex bundlers like Webpack or Vite.

---
## Key Features

* **Simple Setup:** A single command to get you started.
* **Automated Dependency Installation:** Automatically creates a `package.json` and runs `npm install`.
* **Django Integration:** Works seamlessly with `manage.py` commands.
* **Official CLI:** Uses the official `@tailwindcss/cli` for fast and reliable builds.
* **Development Ready:** Includes a `--watch` mode for automatic rebuilding.
* **Production Ready:** Supports CSS minification with a `--minify` flag.

---
## Requirements

* Python 3.8+
* Django 4.2+
* Node.js and npm

---
## Installation

1.  **Install the package from PyPI:**
    ```bash
    pip install django-tailwind-v4
    ```

2.  **Add it to your `INSTALLED_APPS` in `settings.py`:**
    ```python
    # settings.py
    INSTALLED_APPS = [
        # ... other apps
        'django_tailwind_v4',
    ]
    ```

---
## Usage

### 1. Initialize Your Project

Run the `tailwind_init` command. This single command handles the entire setup process for you.

```bash
python manage.py tailwind_init
```

This will:
* Create a `package.json` with the required Tailwind dependencies.
* Create a `tailwind.config.js` file pre-configured for Django templates.
* Create a `static/src/input.css` file with the correct v4 `@import` directive.
* **Automatically run `npm install`** to download the Tailwind CLI.

### 2. Build Your CSS

Run the `tailwind_build` command to compile your CSS. For development, it's highly recommended to use the `--watch` flag in a separate terminal.

```bash
# For development (watches for changes and rebuilds automatically)
python manage.py tailwind_build --watch

# For a single production build (minified)
python manage.py tailwind_build --minify

### 3. Include the CSS in Your Template
```
Finally, link the compiled stylesheet in your base HTML template.

```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Awesome Site</title>
    <link href="{% static 'dist/output.css' %}" rel="stylesheet">
</head>
<body>
    <h1 class="text-3xl font-bold text-blue-600">
        Hello, Tailwind!
    </h1>
</body>
</html>
```
---
## Configuration

While the package works out of the box, you have full control to customize its behavior.

### Customizing Paths

You can change the default input and output CSS paths by adding the following variables to your `settings.py` file. This is useful if you are integrating with an existing theme structure.

```python
# settings.py

# Path to your source CSS file (default is 'static/src/input.css')
TAILWIND_INPUT_CSS = 'themes/mytheme/css/styles.css'

# Path where the compiled CSS will be saved (default is 'static/dist/output.css')
TAILWIND_OUTPUT_CSS = 'themes/mytheme/static/css/styles.css'
```
### Customizing Tailwind CSS

The `tailwind.config.js` file created by the `init` command is a standard Tailwind configuration file. You can edit it to customize your design system.

For example, to add custom colors:
```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './**/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        'brand-blue': '#1992d4',
      },
    },
  },
  plugins: [],
}
```

You can also install and add Tailwind plugins. For example, to add the official forms plugin:

1.  Install the plugin via npm:
    ```bash
    npm install -D @tailwindcss/forms
    ```
2.  Add it to your `tailwind.config.js`:
    ```javascript
    // tailwind.config.js
    module.exports = {
      // ...
      plugins: [
        require('@tailwindcss/forms'),
      ],
    }
    ```

---
## License

This project is licensed under the MIT License. See the `LICENSE` file for details.