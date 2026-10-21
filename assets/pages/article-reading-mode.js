/* LexTalk.Legal TV Frame — lazily creates one accessible reading overlay per open. */
(function () {
  "use strict";
  const trigger = document.querySelector("[data-ltl-reader-open]");
  if (!trigger) return;
  const main = trigger.closest("main.article-wrap");
  if (!main) return;
  let overlay = null;
  let previousOverflow = "";

  function closeReader() {
    if (!overlay) return;
    document.removeEventListener("keydown", onKeyDown);
    overlay.remove();
    overlay = null;
    document.body.classList.remove("ltl-reader-active");
    document.body.style.overflow = previousOverflow;
    trigger.focus();
  }

  function onKeyDown(event) {
    if (event.key === "Escape") {
      event.preventDefault();
      closeReader();
      return;
    }
    if (event.key !== "Tab" || !overlay) return;
    const focusables = Array.from(overlay.querySelectorAll("button,[href],[tabindex]:not([tabindex='-1'])"))
      .filter(element => !element.disabled && element.getClientRects().length);
    if (!focusables.length) return;
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  function cloneArticleContent(target) {
    const selectors = [
      ":scope > .utility-kicker",
      ":scope > h1",
      ":scope > .article-publication-date",
      ":scope > .article-meta",
      ":scope > .article-hero",
      ":scope > .article-body",
      ":scope > .notice",
      ":scope > .article-source"
    ];
    selectors.forEach(selector => {
      const element = main.querySelector(selector);
      if (element) target.appendChild(element.cloneNode(true));
    });

    target.querySelectorAll("script, object, embed").forEach(element => element.remove());

    target.querySelectorAll(".article-x-embed").forEach(embed => {
      const source = embed.querySelector('a[href*="x.com/"]');
      const card = document.createElement("div");
      card.className = "ltl-reader-external";
      if (source) {
        const link = document.createElement("a");
        link.href = source.href;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = "Open the original X post ↗";
        card.appendChild(link);
      } else {
        card.textContent = "The original X post is linked in the source article.";
      }
      embed.replaceWith(card);
    });

    target.querySelectorAll("iframe").forEach(frame => {
      const src = frame.getAttribute("src") || "";
      const card = document.createElement("div");
      card.className = "ltl-reader-external";
      try {
        const parsed = new URL(src, location.href);
        if (parsed.protocol === "https:" || parsed.protocol === "http:") {
          const link = document.createElement("a");
          link.href = parsed.href;
          link.target = "_blank";
          link.rel = "noopener noreferrer";
          link.textContent = "Open referenced media in a new tab ↗";
          card.appendChild(link);
        } else {
          card.textContent = "Embedded media is not shown in reading mode.";
        }
      } catch (_) {
        card.textContent = "Embedded media is not shown in reading mode.";
      }
      frame.replaceWith(card);
    });

    target.querySelectorAll("img").forEach((image, index) => {
      if (index > 0) image.loading = "lazy";
      image.decoding = "async";
    });
  }

  function openReader() {
    if (overlay) return;
    previousOverflow = document.body.style.overflow;
    overlay = document.createElement("div");
    overlay.className = "ltl-reader-overlay";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-labelledby", "ltl-reader-dialog-title");
    overlay.innerHTML =
      '<section class="ltl-reader-window">' +
        '<header class="ltl-reader-topbar">' +
          '<div class="ltl-reader-brand">' +
            '<img src="/assets/LexTalkLegal_Logo-wo-bg.png" alt="Lex Talk Legal">' +
            '<span class="ltl-reader-brand-title" id="ltl-reader-dialog-title">LexTalk.Legal TV Frame</span>' +
          '</div>' +
          '<button type="button" class="ltl-reader-close" aria-label="Close reading frame">✕ <span>Close</span></button>' +
        '</header>' +
        '<div class="ltl-reader-scroll" tabindex="0"><article class="ltl-reader-document"></article></div>' +
      '</section>';

    const documentPane = overlay.querySelector(".ltl-reader-document");
    cloneArticleContent(documentPane);
    overlay.querySelector(".ltl-reader-close").addEventListener("click", closeReader);
    overlay.addEventListener("click", event => {
      if (event.target === overlay) closeReader();
    });
    document.body.appendChild(overlay);
    document.body.classList.add("ltl-reader-active");
    document.body.style.overflow = "hidden";
    document.addEventListener("keydown", onKeyDown);
    overlay.querySelector(".ltl-reader-close").focus();
  }

  trigger.addEventListener("click", openReader);
})();
