import re
import markdown
import uuid
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options


class MarkdownPreviewPlugin(BasePlugin):
    """
    Plugin that converts ```md preview code blocks into side-by-side preview format
    """
    
    config_scheme = (
        ('enable', config_options.Type(bool, default=True)),
        ('left_title', config_options.Type(str, default='Markdown Source')),
        ('right_title', config_options.Type(str, default='Rendered Output')),
    )
    
    def __init__(self):
        self.md_processor = None
        self.html_replacements = {}
    
    def on_config(self, config):
        """Initialize markdown processor with same extensions as main config"""
        # Get markdown extensions from main config
        extensions = config.get('markdown_extensions', [])
        extension_configs = config.get('mdx_configs', {})
        
        # Create a markdown processor with the same extensions
        self.md_processor = markdown.Markdown(
            extensions=extensions,
            extension_configs=extension_configs
        )
        
        return config
    
    def on_page_markdown(self, markdown_content, page, config, files):
        """Process the markdown content before it's converted to HTML"""
        if not self.config['enable']:
            return markdown_content
            
        # Split content by lines to process line by line
        lines = markdown_content.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check if this line starts a md preview block
            if re.match(r'```md\s+preview\s*$', line.strip()):
                # Found start of md preview block
                preview_start = i
                md_source_lines = []
                i += 1
                
                # Collect all lines until we find the closing ```
                backtick_depth = 0
                while i < len(lines):
                    current_line = lines[i]
                    
                    # Check for code block markers
                    if current_line.strip().startswith('```'):
                        if backtick_depth == 0 and current_line.strip() == '```':
                            # This is our closing marker
                            break
                        elif current_line.strip() != '```':
                            # This is a nested code block start
                            backtick_depth += 1
                        elif backtick_depth > 0:
                            # This is a nested code block end
                            backtick_depth -= 1
                    
                    md_source_lines.append(current_line)
                    i += 1
                
                if i < len(lines):  # Found closing ```
                    # Process the markdown content
                    md_source = '\n'.join(md_source_lines)
                    
                    # Reset the markdown processor to avoid state issues
                    self.md_processor.reset()
                    
                    # Render the markdown content to HTML
                    rendered_html = self.md_processor.convert(md_source)
                    
                    # Escape the source for display in HTML - more comprehensive escaping
                    import html
                    escaped_source = html.escape(md_source, quote=True)
                    
                    # Additional escaping for markdown-specific characters that might cause issues
                    escaped_source = (escaped_source
                                    .replace('\u00a0', '&nbsp;')  # Non-breaking space
                                    .replace('\u2026', '&hellip;')  # Ellipsis
                                    .replace('\u2013', '&ndash;')  # En dash
                                    .replace('\u2014', '&mdash;')  # Em dash
                                    .replace('\u2018', '&lsquo;')  # Left single quote
                                    .replace('\u2019', '&rsquo;')  # Right single quote
                                    .replace('\u201c', '&ldquo;')  # Left double quote
                                    .replace('\u201d', '&rdquo;'))  # Right double quote
                    
                    # Create the side-by-side HTML structure
                    side_by_side_html = f'''
<div class="markdown-preview-container">
    <div class="markdown-preview-wrapper">
        <div class="markdown-preview-left">
            <div class="markdown-preview-header">{self.config['left_title']}</div>
            <div class="markdown-preview-content">
                <pre><code class="language-markdown">{escaped_source}</code></pre>
            </div>
        </div>
        <div class="markdown-preview-right">
            <div class="markdown-preview-header">{self.config['right_title']}</div>
            <div class="markdown-preview-content markdown-preview-rendered">
                {rendered_html}
            </div>
        </div>
    </div>
</div>'''
                    
                    # Create a unique placeholder to prevent markdown processing
                    placeholder_id = str(uuid.uuid4())
                    placeholder = f"MARKDOWN_PREVIEW_PLACEHOLDER_{placeholder_id}"
                    
                    # Store the HTML for later replacement
                    self.html_replacements[placeholder] = side_by_side_html
                    
                    # Add the placeholder instead of the HTML
                    result_lines.append(placeholder)
                    i += 1  # Skip the closing ```
                else:
                    # No closing ``` found, treat as regular content
                    result_lines.append(line)
                    i = preview_start + 1
            else:
                result_lines.append(line)
                i += 1
        
        return '\n'.join(result_lines)
    
    def on_page_content(self, html, page, config, files):
        """Replace placeholders with actual HTML after markdown processing"""
        if not self.config['enable']:
            return html
            
        # Replace all placeholders with their corresponding HTML
        for placeholder, replacement_html in self.html_replacements.items():
            html = html.replace(f'<p>{placeholder}</p>', replacement_html)
            html = html.replace(placeholder, replacement_html)
        
        # Clear the replacements for the next page
        self.html_replacements.clear()
        
        return html
