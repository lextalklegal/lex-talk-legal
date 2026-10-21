/* LexTalk.Legal TV Frame — one shared, distraction-free reading window. */
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

    const closingOverlay = overlay;
    document.removeEventListener("keydown", onKeyDown);

    if (document.fullscreenElement === closingOverlay && typeof document.exitFullscreen === "function") {
      try {
        const result = document.exitFullscreen();
        if (result && typeof result.catch === "function") result.catch(function () {});
      } catch (_) {}
    }

    closingOverlay.remove();
    overlay = null;
    document.body.classList.remove("ltl-reader-active");
    document.body.style.overflow = previousOverflow;
    trigger.setAttribute("aria-expanded", "false");
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
      .filter(function (element) { return !element.disabled && element.getClientRects().length; });
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

    selectors.forEach(function (selector) {
      const element = main.querySelector(selector);
      if (element) target.appendChild(element.cloneNode(true));
    });

    target.querySelectorAll("script,object,embed,form").forEach(function (element) { element.remove(); });

    target.querySelectorAll(".article-x-embed").forEach(function (embed) {
      // Rebuild the official X embed markup from its canonical post URL. A cloned
      // tweet may already have been converted to an iframe on the source page, and
      // copying that iframe is unreliable; widgets.js must render a fresh blockquote.
      const source = embed.querySelector('.article-x-embed-head a[href*="x.com/"], a[href*="x.com/"]');
      if (!source) return;

      const postUrl = source.href;
      const replacement = embed.cloneNode(false);
      const header = document.createElement("div");
      header.className = "article-x-embed-head";
      const label = document.createElement("span");
      label.textContent = "ORIGINAL POST";
      const openLink = document.createElement("a");
      openLink.href = postUrl;
      openLink.target = "_blank";
      openLink.rel = "noopener noreferrer";
      openLink.textContent = "Open on X ↗";
      header.append(label, openLink);

      const tweet = document.createElement("blockquote");
      tweet.className = "twitter-tweet";
      tweet.setAttribute("data-conversation", "none");
      tweet.setAttribute("data-dnt", "true");
      const tweetLink = document.createElement("a");
      tweetLink.href = postUrl;
      tweetLink.textContent = "View the original post on X";
      tweet.appendChild(tweetLink);

      const fallback = document.createElement("p");
      fallback.className = "article-x-embed-fallback";
      fallback.appendChild(document.createTextNode("If the post does not load, "));
      const fallbackLink = document.createElement("a");
      fallbackLink.href = postUrl;
      fallbackLink.target = "_blank";
      fallbackLink.rel = "noopener noreferrer";
      fallbackLink.textContent = "open the original on X ↗";
      fallback.appendChild(fallbackLink);
      fallback.appendChild(document.createTextNode("."));

      replacement.append(header, tweet, fallback);
      embed.replaceWith(replacement);
    });

    target.querySelectorAll("iframe").forEach(function (frame) {
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

    target.querySelectorAll("a[href^='http']").forEach(function (link) {
      link.target = "_blank";
      link.rel = "noopener noreferrer";
    });

    target.querySelectorAll("img").forEach(function (image, index) {
      if (index > 0) image.loading = "lazy";
      image.decoding = "async";
    });
  }

  let xWidgetsReady = null;

  function loadXWidgets(target) {
    function renderWidgets() {
      if (!window.twttr || !window.twttr.widgets || typeof window.twttr.widgets.load !== "function") return;
      try {
        const rendered = window.twttr.widgets.load(target);
        if (rendered && typeof rendered.then === "function") {
          rendered.then(function () {
            target.querySelectorAll(".article-x-embed").forEach(function (embed) {
              if (embed.querySelector("iframe")) {
                const fallback = embed.querySelector(".article-x-embed-fallback");
                if (fallback) fallback.hidden = true;
              }
            });
          }).catch(function () {});
        }
      } catch (_) {}
    }

    if (window.twttr && window.twttr.widgets && typeof window.twttr.widgets.load === "function") {
      renderWidgets();
      return;
    }

    if (!xWidgetsReady) {
      xWidgetsReady = new Promise(function (resolve, reject) {
        const script = document.createElement("script");
        script.async = true;
        script.charset = "utf-8";
        script.src = "https://platform.twitter.com/widgets.js";
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
      }).catch(function () {
        // Keep the visible direct-to-X link as a fallback if the embed is blocked.
      });
    }
    xWidgetsReady.then(renderWidgets);
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
        '<footer class="ltl-reader-footer"><span>LAW. CONTEXT. CLARITY.</span><span>lextalk.legal</span></footer>' +
      '</section>';

    const documentPane = overlay.querySelector(".ltl-reader-document");
    cloneArticleContent(documentPane);

    overlay.querySelector(".ltl-reader-close").addEventListener("click", closeReader);
    overlay.addEventListener("click", function (event) {
      if (event.target === overlay) closeReader();
    });

    document.body.appendChild(overlay);
    loadXWidgets(documentPane);
    document.body.classList.add("ltl-reader-active");
    document.body.style.overflow = "hidden";
    trigger.setAttribute("aria-expanded", "true");
    document.addEventListener("keydown", onKeyDown);

    // Browser Fullscreen API hides Chrome's address bar while this reading window is open.
    // If fullscreen is denied by the browser, keep the same overlay as a safe fallback.
    if (typeof overlay.requestFullscreen === "function") {
      try {
        const request = overlay.requestFullscreen({ navigationUI: "hide" });
        if (request && typeof request.catch === "function") {
          request.catch(function () {
            if (overlay) overlay.classList.add("ltl-reader-fallback");
          });
        }
      } catch (_) {
        overlay.classList.add("ltl-reader-fallback");
      }
    } else {
      overlay.classList.add("ltl-reader-fallback");
    }

    overlay.querySelector(".ltl-reader-close").focus();
    overlay.querySelector(".ltl-reader-scroll").scrollTop = 0;
  }

  trigger.setAttribute("aria-haspopup", "dialog");
  trigger.setAttribute("aria-expanded", "false");
  trigger.addEventListener("click", openReader);
})();
