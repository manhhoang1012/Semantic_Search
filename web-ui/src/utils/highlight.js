export function escapeHtml(unsafe) {
    return (unsafe || "").toString()
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

export function removeAccents(str) {
  return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
}

export function highlightText(text, query) {
  if (!text) return "";
  if (!query) return escapeHtml(text);
  
  const words = query.split(/\s+/).filter(w => w.trim().length > 0);
  if (words.length === 0) return escapeHtml(text);

  const strippedText = removeAccents(text);
  const sortedWords = words.map(removeAccents).sort((a, b) => b.length - a.length);
  
  let matchRanges = [];
  
  for (const word of sortedWords) {
    if (word.length < 2) continue; // Skip single characters to avoid noisy highlights
    
    let startIndex = 0;
    while ((startIndex = strippedText.indexOf(word, startIndex)) !== -1) {
      matchRanges.push({ start: startIndex, end: startIndex + word.length });
      startIndex += word.length;
    }
  }
  
  matchRanges.sort((a, b) => a.start - b.start);
  const mergedRanges = [];
  for (const range of matchRanges) {
    if (mergedRanges.length === 0) {
      mergedRanges.push(range);
    } else {
      const last = mergedRanges[mergedRanges.length - 1];
      if (range.start <= last.end) {
        last.end = Math.max(last.end, range.end);
      } else {
        mergedRanges.push(range);
      }
    }
  }
  
  let lastIndex = 0;
  let resultHtml = "";
  
  for (const range of mergedRanges) {
    // Unmatched chunk
    resultHtml += escapeHtml(text.substring(lastIndex, range.start));
    // Matched chunk
    resultHtml += `<span class="bg-yellow-500/30 text-yellow-200 rounded px-0.5">` + 
                  escapeHtml(text.substring(range.start, range.end)) + 
                  `</span>`;
    lastIndex = range.end;
  }
  // Remaining text
  resultHtml += escapeHtml(text.substring(lastIndex));
  
  return resultHtml;
}
