# ShadowHawk Database Browser - Product Website

Welcome to the official product website for ShadowHawk Database Browser v1.0.0!

## 🌐 Website Overview

This is a professional, responsive product website built with modern web technologies to showcase the ShadowHawk Database Browser application.

### ✨ Features

- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Professional UI**: Built with Bootstrap 5 and custom CSS animations
- **Interactive Elements**: Smooth scrolling, hover effects, and dynamic content
- **Performance Chart**: Visual comparison showing ShadowHawk's speed advantages
- **Download Integration**: Direct links to GitHub releases and source code
- **Documentation Links**: Easy access to all project documentation

### 🛠️ Technology Stack

- **HTML5**: Semantic markup with accessibility features
- **CSS3**: Custom styles with CSS Grid, Flexbox, and animations
- **Bootstrap 5**: Responsive framework and components
- **JavaScript (ES6+)**: Interactive functionality and animations
- **Chart.js**: Performance visualization
- **Bootstrap Icons**: Consistent iconography

## 📁 Project Structure

```
docs/website/
├── index.html          # Main website page
├── css/
│   └── style.css      # Custom styles and animations
├── js/
│   └── script.js      # Interactive functionality
├── assets/
│   ├── README.md      # Guide for adding screenshots
│   └── [screenshots]  # Application screenshots (to be added)
└── README.md          # This file
```

## 🚀 Getting Started

### Viewing the Website

1. **Local Development**:
   ```bash
   # Navigate to the website directory
   cd docs/website
   
   # Open in browser (or use a local server)
   # For simple viewing:
   open index.html
   
   # For development with live reload:
   python -m http.server 8000
   # Then visit: http://localhost:8000
   ```

2. **Live Server** (recommended for development):
   - Install a live server extension in your code editor
   - Open the `index.html` file
   - The website will auto-reload on changes

### Adding Screenshots

The website is designed to showcase the application with real screenshots. To add them:

1. **Take Application Screenshots**:
   - Run ShadowHawk Database Browser
   - Load sample databases (SQLite, CSV, Excel)
   - Capture high-quality screenshots (1200x800px recommended)

2. **Required Screenshots**:
   - `app-screenshot.png` - Main hero image
   - `screenshot-main.png` - Main interface
   - `screenshot-search.png` - Global search feature
   - `screenshot-analysis.png` - Data analysis view

3. **Place in Assets Folder**:
   ```bash
   # Add screenshots to:
   docs/website/assets/
   ```

4. **See `assets/README.md`** for detailed guidelines

## 🎨 Customization

### Styling

The website uses a custom CSS framework built on top of Bootstrap:

- **Colors**: Defined in CSS custom properties (`:root`)
- **Animations**: Custom keyframe animations for smooth interactions
- **Responsive**: Mobile-first responsive design
- **Themes**: Easy to customize color schemes

### Content Updates

Key sections to update for new releases:

1. **Version Numbers**: Update throughout `index.html`
2. **Feature Lists**: Modify in the features section
3. **Performance Stats**: Update the Chart.js data
4. **Download Links**: Ensure GitHub links are current

### Adding New Sections

The website is modular and easy to extend:

```html
<section id="new-section" class="py-5">
    <div class="container">
        <!-- Your content here -->
    </div>
</section>
```

## 📱 Responsive Design

The website is fully responsive and tested on:

- **Desktop**: 1920px+ (full features)
- **Laptop**: 1024px-1919px (optimized layout)
- **Tablet**: 768px-1023px (stacked layout)
- **Mobile**: 320px-767px (single column)

## ⚡ Performance

- **Optimized Images**: Compressed for fast loading
- **Minified Assets**: CSS and JS optimized for production
- **CDN Resources**: Bootstrap and Chart.js from CDN
- **Lazy Loading**: Images load on scroll
- **Smooth Animations**: Hardware-accelerated CSS animations

## 🔗 SEO & Accessibility

- **Meta Tags**: Complete SEO meta tags
- **Open Graph**: Social media preview optimization
- **Semantic HTML**: Proper heading structure and landmarks
- **Alt Text**: Descriptive alt text for all images
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader**: ARIA labels and semantic markup

## 🚀 Deployment

### GitHub Pages

The website can be deployed to GitHub Pages:

1. **Enable GitHub Pages** in repository settings
2. **Set source** to `docs/website` folder
3. **Custom Domain** (optional): Configure in repository settings

### Manual Deployment

For other hosting providers:

1. **Upload Files**: Copy `docs/website/` contents to web server
2. **Configure Server**: Ensure proper MIME types for all files
3. **SSL Certificate**: Enable HTTPS for security
4. **CDN** (optional): Use CDN for global performance

## 🐛 Troubleshooting

### Common Issues

1. **Images Not Loading**:
   - Check file paths in `assets/` folder
   - Verify image file names match HTML references
   - Ensure images are optimized for web

2. **JavaScript Not Working**:
   - Check browser console for errors
   - Verify Bootstrap JS is loading from CDN
   - Test in different browsers

3. **Responsive Issues**:
   - Test in browser developer tools
   - Check Bootstrap grid classes
   - Verify CSS custom properties support

### Browser Support

- **Modern Browsers**: Chrome 80+, Firefox 75+, Safari 13+, Edge 80+
- **CSS Features**: Grid, Flexbox, Custom Properties
- **JavaScript**: ES6+ features (const, let, arrow functions)

## 🤝 Contributing

To improve the website:

1. **Fork** the repository
2. **Create** a feature branch
3. **Make changes** to HTML, CSS, or JS
4. **Test** on multiple devices and browsers
5. **Submit** a pull request

### Development Guidelines

- **Mobile First**: Design for mobile, enhance for desktop
- **Performance**: Optimize images and minimize HTTP requests
- **Accessibility**: Test with screen readers and keyboard navigation
- **Cross-Browser**: Test in major browsers
- **Code Quality**: Use consistent indentation and comments

## 📄 License

This website is part of the ShadowHawk Database Browser project and is licensed under the MIT License. See the main project `LICENSE` file for details.

## 🙏 Credits

- **Bootstrap Team**: For the excellent CSS framework
- **Chart.js Team**: For the performance visualization library
- **Bootstrap Icons**: For the comprehensive icon set
- **ShadowHawk Team**: For the amazing database browser application

---

**Built with ❤️ for the ShadowHawk Database Browser community**
