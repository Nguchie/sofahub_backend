/**
 * Product Variation Autocomplete
 * Injects HTML5 datalist elements for color, material, and size suggestions
 */

(function() {
    'use strict';
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAutocomplete);
    } else {
        initAutocomplete();
    }
    
    function initAutocomplete() {
        // Color suggestions
        const colorSuggestions = [
            'Black', 'White', 'Gray', 'Charcoal', 'Silver',
            'Brown', 'Tan', 'Beige', 'Cream', 'Ivory',
            'Red', 'Burgundy', 'Maroon',
            'Blue', 'Navy', 'Teal', 'Turquoise',
            'Green', 'Olive', 'Sage',
            'Yellow', 'Gold', 'Mustard',
            'Orange', 'Rust', 'Terracotta',
            'Purple', 'Plum', 'Lavender',
            'Pink', 'Rose', 'Blush',
            'Walnut', 'Oak', 'Cherry', 'Mahogany', 'Espresso',
            'Natural Wood', 'Light Wood', 'Dark Wood',
            'Multi-Color', 'Patterned', 'Two-Tone'
        ];
        
        // Material suggestions
        const materialSuggestions = [
            'Leather', 'Genuine Leather', 'Bonded Leather', 'Faux Leather',
            'Fabric', 'Linen', 'Cotton', 'Velvet', 'Microfiber', 'Suede',
            'Wood', 'Solid Wood', 'Oak', 'Pine', 'Walnut', 'Teak', 'Mahogany',
            'Engineered Wood', 'MDF', 'Plywood', 'Particle Board',
            'Metal', 'Steel', 'Aluminum', 'Iron', 'Brass', 'Chrome',
            'Glass', 'Tempered Glass', 'Frosted Glass',
            'Marble', 'Granite', 'Quartz',
            'Rattan', 'Wicker', 'Bamboo', 'Cane',
            'Plastic', 'Acrylic', 'Resin',
            'Upholstered', 'Foam', 'Memory Foam',
            'Mixed Materials', 'Wood & Metal', 'Fabric & Wood'
        ];
        
        // Size suggestions
        const sizeSuggestions = [
            // Bed sizes
            'King Size', 'Queen Size', 'Full/Double', 'Twin/Single', 'California King',
            // General sizes
            'Small', 'Medium', 'Large', 'Extra Large',
            // Seating
            '2-Seater', '3-Seater', '4-Seater', '5-Seater', 'L-Shape', 'U-Shape',
            // Tables
            '4-Person', '6-Person', '8-Person', '10-Person', '12-Person',
            // Dimensions
            '120cm', '150cm', '180cm', '200cm', '240cm',
            // Storage
            '2-Door', '3-Door', '4-Door', '5-Drawer', '6-Drawer',
            // Other
            'Compact', 'Standard', 'Oversized', 'Custom Size'
        ];
        
        // Create datalist elements if they don't exist
        createDatalist('color-suggestions', colorSuggestions);
        createDatalist('material-suggestions', materialSuggestions);
        createDatalist('size-suggestions', sizeSuggestions);
    }
    
    function createDatalist(id, suggestions) {
        // Remove existing datalist if present
        const existing = document.getElementById(id);
        if (existing) {
            existing.remove();
        }
        
        // Create new datalist
        const datalist = document.createElement('datalist');
        datalist.id = id;
        
        // Add options
        suggestions.forEach(function(suggestion) {
            const option = document.createElement('option');
            option.value = suggestion;
            datalist.appendChild(option);
        });
        
        // Append to body
        document.body.appendChild(datalist);
    }
    
    // Re-initialize when Django adds new inline forms
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).on('formset:added', function() {
            initAutocomplete();
        });
    }
})();

