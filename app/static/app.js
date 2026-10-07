document.addEventListener('DOMContentLoaded', () => {
  const chatFeed = document.getElementById('chatFeed');
  const questionForm = document.getElementById('questionForm');
  const questionInput = document.getElementById('questionInput');
  const sendBtn = document.getElementById('sendBtn');
  const welcomeBox = document.getElementById('welcomeBox');
  const clearChatBtn = document.getElementById('clearChatBtn');

  // Sample question chip clicks
  document.querySelectorAll('.sample-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const text = chip.innerText.split('\n')[1] || chip.innerText;
      questionInput.value = text.trim();
      submitQuestion(text.trim());
    });
  });

  // Clear chat history
  clearChatBtn.addEventListener('click', () => {
    chatFeed.innerHTML = '';
    if (welcomeBox) chatFeed.appendChild(welcomeBox);
  });

  // Form submission
  questionForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const question = questionInput.value.trim();
    if (!question) return;
    submitQuestion(question);
  });

  async function submitQuestion(question) {
    // Hide welcome hero box on first question
    if (welcomeBox && chatFeed.contains(welcomeBox)) {
      welcomeBox.remove();
    }

    // Append User Message Bubble
    appendUserMessage(question);
    questionInput.value = '';
    sendBtn.disabled = true;

    // Append Loading Indicator
    const loadingId = appendLoadingMessage();

    try {
      const response = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });

      const data = await response.json();
      removeMessage(loadingId);

      if (response.ok) {
        appendAiMessage(data.answer, data.citations);
      } else {
        const errorMsg = data.detail?.[0]?.msg || data.detail || 'Failed to process question.';
        appendErrorMessage(errorMsg);
      }
    } catch (err) {
      removeMessage(loadingId);
      appendErrorMessage('Network error: Unable to connect to Ask My Docs API.');
    } finally {
      sendBtn.disabled = false;
      questionInput.focus();
    }
  }

  function appendUserMessage(text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'flex justify-end max-w-3xl mx-auto';
    msgDiv.innerHTML = `
      <div class="bg-brand-600 text-slate-950 font-medium px-5 py-3.5 rounded-2xl rounded-tr-none shadow-md max-w-xl">
        <p class="text-sm leading-relaxed">${escapeHtml(text)}</p>
      </div>
    `;
    chatFeed.appendChild(msgDiv);
    chatFeed.scrollTop = chatFeed.scrollHeight;
  }

  function appendAiMessage(answer, citations) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'flex items-start gap-4 max-w-3xl mx-auto';

    const isUnanswerable = citations.length === 0;
    const parsedAnswer = typeof marked !== 'undefined' ? marked.parse(answer) : answer;

    let citationBadgesHtml = '';

    if (citations && citations.length > 0) {
      citationBadgesHtml = `
        <div class="mt-4 pt-3 border-t border-slate-800/60 flex flex-wrap gap-2 items-center">
          <span class="text-xs font-semibold text-slate-400">Sources:</span>
          ${citations.map(c => `
            <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
              <i class="fa-solid fa-file-pdf"></i> ${escapeHtml(c.source)} (Page ${c.page})
            </span>
          `).join('')}
        </div>
      `;
    } else {
      citationBadgesHtml = `
        <div class="mt-4 pt-3 border-t border-slate-800/60 flex items-center gap-2">
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs">
            <i class="fa-solid fa-triangle-exclamation"></i> Grounded Fallback: No matching document context
          </span>
        </div>
      `;
    }

    msgDiv.innerHTML = `
      <div class="w-9 h-9 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-brand-400 shrink-0 mt-1 shadow-md">
        <i class="fa-solid fa-robot"></i>
      </div>
      <div class="bg-slate-900/80 border border-slate-800/80 text-slate-200 px-6 py-4 rounded-2xl rounded-tl-none shadow-lg flex-1">
        <div class="prose prose-invert text-sm leading-relaxed">${parsedAnswer}</div>
        ${citationBadgesHtml}
      </div>
    `;

    chatFeed.appendChild(msgDiv);
    chatFeed.scrollTop = chatFeed.scrollHeight;
  }

  function appendLoadingMessage() {
    const id = 'loading-' + Date.now();
    const msgDiv = document.createElement('div');
    msgDiv.id = id;
    msgDiv.className = 'flex items-start gap-4 max-w-3xl mx-auto';
    msgDiv.innerHTML = `
      <div class="w-9 h-9 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-brand-400 shrink-0 mt-1 shadow-md">
        <i class="fa-solid fa-robot animate-spin"></i>
      </div>
      <div class="bg-slate-900/80 border border-slate-800/80 text-slate-400 px-5 py-3.5 rounded-2xl rounded-tl-none text-xs flex items-center gap-3">
        <div class="flex gap-1">
          <span class="w-1.5 h-1.5 rounded-full bg-brand-400 animate-bounce"></span>
          <span class="w-1.5 h-1.5 rounded-full bg-brand-400 animate-bounce [animation-delay:0.2s]"></span>
          <span class="w-1.5 h-1.5 rounded-full bg-brand-400 animate-bounce [animation-delay:0.4s]"></span>
        </div>
        <span>Hybrid retrieval & reranking context...</span>
      </div>
    `;
    chatFeed.appendChild(msgDiv);
    chatFeed.scrollTop = chatFeed.scrollHeight;
    return id;
  }

  function appendErrorMessage(errorMsg) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'flex items-start gap-4 max-w-3xl mx-auto';
    msgDiv.innerHTML = `
      <div class="w-9 h-9 rounded-xl bg-red-950 border border-red-800 flex items-center justify-center text-red-400 shrink-0 mt-1 shadow-md">
        <i class="fa-solid fa-circle-exclamation"></i>
      </div>
      <div class="bg-red-950/40 border border-red-800/60 text-red-300 px-5 py-3.5 rounded-2xl rounded-tl-none text-xs">
        <p class="font-semibold mb-0.5">API Error</p>
        <p>${escapeHtml(errorMsg)}</p>
      </div>
    `;
    chatFeed.appendChild(msgDiv);
    chatFeed.scrollTop = chatFeed.scrollHeight;
  }

  function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function escapeHtml(str) {
    return str.replace(/[&<>'"]/g, 
      tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
  }
});
