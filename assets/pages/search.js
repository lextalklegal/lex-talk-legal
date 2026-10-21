/* Lex Talk Legal — robust client-side full-text search */
(() => {
  'use strict';
  const input = document.getElementById('siteSearchInput');
  const form = document.getElementById('siteSearchForm');
  const button = document.getElementById('siteSearchBtn');
  const results = document.getElementById('searchResults');
  const meta = document.getElementById('searchMeta');
  if (!input || !form || !results || !meta) return;

  const normalize = value => String(value || '')
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .toLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
  const stripHtml = value => {
    const node = document.createElement('div');
    node.innerHTML = String(value || '');
    return node.textContent || node.innerText || '';
  };
  const escapeText = value => String(value || '');
  const dateValue = article => {
    const date = Date.parse(article.published || article.updated || '');
    return Number.isFinite(date) ? date : 0;
  };
  const safeArticleUrl = value => {
    const url = String(value || '').trim();
    if (!url.startsWith('/') || url.startsWith('//') || url.includes('\\')) return '';
    return url;
  };
  const searchableText = article => normalize([
    article.title, article.excerpt, article.meta_description, article.description,
    article.category, ...(Array.isArray(article.labels) ? article.labels : []),
    article.tags, stripHtml(article.content)
  ].flat().join(' '));

  let index = [];
  let loaded = false;
  let debounceId;
  let lastQuery = '';
  const make = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = escapeText(text);
    return node;
  };
  function showEmpty(message) {
    results.replaceChildren(make('div', 'empty', message));
  }
  function render(query) {
    const normalized = normalize(query);
    lastQuery = query;
    results.replaceChildren();
    if (!loaded) {
      meta.textContent = 'Loading searchable articles…';
      showEmpty('Preparing the search index…');
      return;
    }
    if (!normalized) {
      meta.textContent = index.length + ' articles indexed. Enter a keyword to begin.';
      showEmpty('Search titles, article text, categories, keywords and labels.');
      return;
    }
    const terms = [...new Set(normalized.split(/\s+/).filter(Boolean))];
    const found = [];
    for (const row of index) {
      const hits = terms.filter(term => row.text.includes(term));
      if (hits.length !== terms.length) continue;
      let score = 0;
      for (const term of terms) {
        if (row.titleNorm.includes(term)) score += 12;
        if (row.categoryNorm.includes(term)) score += 5;
        if (row.labelsNorm.includes(term)) score += 4;
        if (row.excerptNorm.includes(term)) score += 3;
        if (row.text.includes(term)) score += 1;
      }
      found.push({ ...row, score });
    }
    found.sort((a, b) => b.score - a.score || b.date - a.date);
    const shown = found.slice(0, 30);
    meta.textContent = found.length
      ? 'Showing ' + shown.length + ' of ' + found.length + ' matching article' + (found.length === 1 ? '' : 's')
      : 'No results for “' + query.trim() + '”. Try fewer or different keywords.';
    if (!shown.length) {
      showEmpty('No matching stories found. Try a court name, legal section, shorter phrase or one keyword.');
      return;
    }
    const fragment = document.createDocumentFragment();
    for (const row of shown) {
      const article = make('article', 'search-result');
      const metaLine = make('div', 'story-meta', (row.category || 'Legal News') + (row.published ? ' · ' + row.published.slice(0, 10) : ''));
      const heading = make('h2');
      const href = safeArticleUrl(row.url);
      if (href) {
        const link = make('a', '', row.title || 'Untitled article');
        link.href = href;
        heading.append(link);
      } else {
        heading.textContent = row.title || 'Untitled article';
      }
      const excerpt = make('p', '', row.excerpt || row.meta_description || '');
      article.append(metaLine, heading, excerpt);
      fragment.append(article);
    }
    results.append(fragment);
  }

  form.addEventListener('submit', event => {
    event.preventDefault();
    render(input.value);
    const url = new URL(location.href);
    if (input.value.trim()) url.searchParams.set('q', input.value.trim());
    else url.searchParams.delete('q');
    history.replaceState(null, '', url.pathname + url.search + url.hash);
  });
  input.addEventListener('input', () => {
    clearTimeout(debounceId);
    debounceId = setTimeout(() => render(input.value), 140);
  });
  button?.addEventListener('click', () => render(input.value));

  const initialQuery = new URLSearchParams(location.search).get('q') || '';
  input.value = initialQuery;
  fetch('/data/articles.json', { cache: 'no-cache' })
    .then(response => {
      if (!response.ok) throw new Error('Search index returned HTTP ' + response.status);
      return response.json();
    })
    .then(data => {
      if (!Array.isArray(data)) throw new Error('Search index has an unexpected format');
      index = data.map(article => {
        const content = stripHtml(article.content || '');
        const labelsNorm = normalize(Array.isArray(article.labels) ? article.labels.join(' ') : article.labels || '');
        const categoryNorm = normalize(article.category || '');
        const titleNorm = normalize(article.title || '');
        const excerptNorm = normalize(article.excerpt || article.meta_description || '');
        return { ...article, titleNorm, categoryNorm, labelsNorm, excerptNorm, text: searchableText({ ...article, content }), date: dateValue(article) };
      }).filter(article => safeArticleUrl(article.url));
      loaded = true;
      render(initialQuery);
    })
    .catch(error => {
      console.error('Lex Talk Legal search index failed:', error);
      meta.textContent = 'Search index could not be loaded.';
      showEmpty('Search is temporarily unavailable. Please refresh the page or try again later.');
    });
})();
