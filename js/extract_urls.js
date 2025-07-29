function normalizeUrl(url) {
    try {
      return new URL(url, document.location).href;
    } catch (e) {
      return null;
    }
  }

  // Collect anchor links with href attribute
  const linkElements = Array.from(document.body.querySelectorAll('a[href]'));
  const links = linkElements.map(a => {
    const href = normalizeUrl(a.getAttribute('href'));
    return {
      type: 'link',
      href: href,
      target: a.getAttribute('target') || null
    };
  }).filter(item => item.href); // Filter out any that couldn't be normalized

  // Collect form elements with an action attribute (if action is missing, it defaults to the current URL)
  const formElements = Array.from(document.body.querySelectorAll('form'));
  const forms = formElements.map(form => {
    let action = form.getAttribute('action');
    // If there's no action defined, assume the current page URL.
    let normalizedAction = action ? normalizeUrl(action) : document.location.href;
    return {
      type: 'form',
      action: normalizedAction,
      target: form.getAttribute('target') || null
    };
  });

  // Combine both results
  const results = {
    links: links,
    forms: forms
  };

  console.log(results);
  return results;