## =========================================================
## Copyright 2019 Dietrich Bollmann
## 
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
## 
##      http://www.apache.org/licenses/LICENSE-2.0
## 
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
## ---------------------------------------------------------

"""newskylabs/graphics/svg/svg.py:

A class for assembling SVG files.

"""

__author__      = "Dietrich Bollmann"
__email__       = "dietrich@formgames.org"
__copyright__   = "Copyright 2019 Dietrich Bollmann"
__license__     = "Apache License 2.0, http://www.apache.org/licenses/LICENSE-2.0"
__date__        = "2019/12/14"

import importlib

from newskylabs.graphics.xml.xml import XMLElement
from newskylabs.graphics.css.css import CSSRule

## =========================================================
## class SVGElement
## ---------------------------------------------------------

class SVGElement(XMLElement):
    """
    SVGElement
    """

    _namespace = 'http://www.w3.org/2000/svg'
    _root_tag = 'svg'

    def __init__(self, tag, *args, **kwargs):
        super().__init__(tag, *args, **kwargs)

    @classmethod
    def root(cls, 
             *args, 
             x=0, y=0, width=100, height=100,
             version='1.1', 
             **kwargs
    ):
        viewBox = '{} {} {} {}'.format(x, y, width, height)

        if 'absolute' in kwargs:
            absolute = kwargs['absolute']
            del kwargs['absolute']

            if absolute:
                kwargs['width']  = '{}mm'.format(width)
                kwargs['height'] = '{}mm'.format(height)
        
        root = super().root(
            *args, 
            version = version, 
            viewBox = viewBox,
            **kwargs
        )
        return root

    def addTransform(self, transform):
        child = SVGElement('g', transform=transform)
        self.append(child)
        return child

    def addTranslate(self, x=0, y=0):
        transform = 'translate({}, {})'.format(x, y)
        child = self.addTransform(transform)
        return child

    def addScale(self, x=None, y=None):

        # When no scaling factor is given 
        # use 1 to scale both dimensions
        if not x:
            x = 1

        if y:
            # Scale both dimensions independently
            transform = 'scale({} {})'.format(x, y)

        else:
            # Scale both dimensions equally
            transform = 'scale({})'.format(x)

        child = self.addTransform(transform)
        return child

    def _format_path(self, path, close_path=False):

        p = path[0]
        pathstr = 'M{} {}'.format(p[0], p[1])
        for p in path[1:]:
            pathstr += ' L{} {}'.format(p[0], p[1])

        pathstr += 'Z' if close_path else ''
    
        return pathstr

    def addPath(self, path=[], *args, close_path=False, **kwargs):
        tag = 'path'
        pathstr = self._format_path(path, close_path=close_path)
        return self.addElement(tag, *args, d=pathstr, **kwargs)
    
    def addText(self, *args, **kwargs):
        
        # Convert 'css-class' etc. to 'class'
        for key in ['css-class', 'css_class', 'cssClass',
                    'class-name', 'class_name', 'className']:
            if key in kwargs:
                kwargs['class'] = kwargs[key]
                del kwargs[key]

        tag = 'text'
        return self.addElement(tag, *args, **kwargs)
    
    def addElement(self, tag, *args, **kwargs):

        child = SVGElement(tag, *args, **kwargs)
        self.append(child)
        return child

    def addQRCode(self, 
                  data,
                  x      = 0,
                  y      = 0,
                  width  = 10,
                  height = 10,
    ):
        # Convert the data to a VCard
        from newskylabs.graphics.svg.library.vcard import VCard
        vcard = VCard(data)

        # Convert to a QRCode object
        qr_code = vcard.to_QRCode()

        # DEBUG
        #| print("DEBUG SVGElement.addQRCode(): QR-Code data:\n\n{}".format(qr_code.get_data()))

        # Convert to SVGElement
        child = qr_code.to_SVGElement(x=x, y=y, width=width, height=height)

        # And append it
        self.append(child)

        # Return the plugin for method chaining
        return child

        #| child = SVGElement(tag, *args, **kwargs)

    def addCSSRule(self, selector, *args, **kwargs):

        # Create a new CSS rule element with the given name
        rule = CSSRule(selector, *args, **kwargs)
        depth = self.depth()

        # Convert it to a string
        rulestr = rule.tostring(level=depth)

        # If this is the first CSS rule
        # add newline after <style> 
        # and initial indent
        if not self._xml.text:
            self._xml.text = '\n' + ' ' * (2 * depth)

        # Add it to the parent as text
        self._xml.text += rulestr

    def addPlugin(self, plugin, *args, debug=0, **kwargs):

        # Get plugin class and parameters
        plugin_class = plugin['class']
        del plugin['class']
        plugin_params = plugin

        # Overwrite parameters given in kwargs
        for param, value in kwargs.items():
            if not param in ['debug']:
                plugin_params[param] = value
            
        if debug > 0:
            print("DEBUG SVGElement.addPlugin(): plugin_params:", plugin_params)

        # Load plugin class dynamically 
        plugin_class_path = plugin_class.split('.')
        module_name = '.'.join(plugin_class_path[:-1])
        class_name = plugin_class_path[-1]
        module = importlib.import_module(module_name)
        plugin_class = getattr(module, class_name)
        
        # Assemble the plugin
        plugin = plugin_class(**plugin_params)
        child = plugin.toSVG()

        # Append the plugin
        self.append(child)

        # Return the plugin for method chaining
        return child

    def __getattr__(self, name):
        
        # When `name' starts with 'add' add a child
        if name[:3] == 'add':
        
            # addSomeClass -> someClass
            name = name[3].lower() + name[4:]
        
            def addElement(*args, **kwargs):
                return self.addElement(name, *args, **kwargs)
        
            return addElement

        # No idea what to do with the attribute
        className = type(self).__name__
        raise AttributeError("An {} has no attribute '{}'"\
                             .format(className, name))

## =========================================================
## =========================================================

## fin
