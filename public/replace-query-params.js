// Zamienia "Query Parameters" na "Parameters"
(function() {
    'use strict';
    
    function replaceQueryParameters() {
        try {
            const headings = document.querySelectorAll('h4.api-section-heading-title');
            let replaced = 0;
            
            headings.forEach(function(heading) {
                if (heading && heading.textContent && heading.textContent.trim() === 'Query Parameters') {
                    heading.textContent = 'Parameters';
                    replaced++;
                }
            });
            
            console.log('Replaced', replaced, 'Query Parameters headings');
        } catch (e) {
            console.error('Error replacing Query Parameters:', e);
        }
    }
    
    // Próbuj wielokrotnie
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', replaceQueryParameters);
    } else {
        replaceQueryParameters();
    }
    
    window.addEventListener('load', replaceQueryParameters);
    setTimeout(replaceQueryParameters, 100);
    setTimeout(replaceQueryParameters, 300);
    setTimeout(replaceQueryParameters, 500);
    setTimeout(replaceQueryParameters, 1000);
    setTimeout(replaceQueryParameters, 2000);
    
    // Observer dla dynamicznych zmian
    if (typeof MutationObserver !== 'undefined') {
        var observer = new MutationObserver(function() {
            replaceQueryParameters();
        });
        
        if (document.body) {
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        } else {
            setTimeout(function() {
                if (document.body) {
                    observer.observe(document.body, {
                        childList: true,
                        subtree: true
                    });
                }
            }, 100);
        }
    }
    
    // Tag Body sections so CSS can hide them precisely
    function tagBodySections() {
        try {
            var sections = document.querySelectorAll('.api-section');
            sections.forEach(function(section) {
                var heading = section.querySelector('h4.api-section-heading-title');
                if (heading && heading.textContent && heading.textContent.trim().toLowerCase() === 'body') {
                    section.setAttribute('data-section', 'body');
                }
            });
        } catch (e) {
            // no-op
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', tagBodySections);
    } else {
        tagBodySections();
    }

    if (typeof MutationObserver !== 'undefined') {
        var bodyObserver = new MutationObserver(function() {
            tagBodySections();
        });
        if (document.documentElement) {
            bodyObserver.observe(document.documentElement, { childList: true, subtree: true });
        }
    }
})();

