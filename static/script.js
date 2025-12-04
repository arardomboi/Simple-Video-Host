document.addEventListener('DOMContentLoaded', ()=>{
  const player = document.getElementById('player');
  const source = document.getElementById('source');

  document.querySelectorAll('.playBtn').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const file = btn.dataset.file;
      source.src = '/video/' + encodeURIComponent(file);
      player.load();
      player.play().catch(()=>{});
    });
  });

  const fsBtn = document.getElementById('fsBtn');
  if(fsBtn){
    fsBtn.addEventListener('click', ()=>{
      if (!document.fullscreenElement) {
        player.requestFullscreen().catch(()=>{});
      } else {
        document.exitFullscreen().catch(()=>{});
      }
    });
  }

  const speedSel = document.getElementById('speed');
  if(speedSel){
    speedSel.addEventListener('change', (e)=>{
      player.playbackRate = parseFloat(e.target.value);
    });
  }

  // Double-click player to fullscreen
  if(player){
    player.addEventListener('dblclick', ()=>{
      if (!document.fullscreenElement) player.requestFullscreen().catch(()=>{});
    });
  }

  // Theme handling: default to dark, allow toggle and persist in localStorage
  const themeToggle = document.getElementById('themeToggle');
  function applyTheme(t){
    if(t === 'light') document.documentElement.setAttribute('data-theme','light');
    else document.documentElement.removeAttribute('data-theme');
  }
  const saved = localStorage.getItem('theme') || 'dark';
  applyTheme(saved);
  if(themeToggle) themeToggle.textContent = saved === 'light' ? 'Light' : 'Dark';
  if(themeToggle){
    themeToggle.addEventListener('click', ()=>{
      const current = localStorage.getItem('theme') || 'dark';
      const next = current === 'light' ? 'dark' : 'light';
      localStorage.setItem('theme', next);
      applyTheme(next);
      themeToggle.textContent = next === 'light' ? 'Light' : 'Dark';
    });
  }
});
