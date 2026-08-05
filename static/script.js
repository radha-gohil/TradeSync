document.addEventListener('DOMContentLoaded', function () {
    const cursorGlow = document.querySelector('.cursor-glow');
  
    document.addEventListener('mousemove', (e) => {
      cursorGlow.style.transform = `translate(${e.clientX - 75}px, ${e.clientY - 75}px)`;
    });
  
    const inputs = document.querySelectorAll('input');
    const character = document.querySelector('.character-svg');
  
    inputs.forEach((input) => {
      input.addEventListener('focus', (e) => {
        if (character) {
          if (e.target.type === 'text') {
            character.classList.add('look-at-input');
          } else if (e.target.type === 'password') {
            character.classList.add('hide-eyes');
          }
        }
      });
  
      input.addEventListener('blur', () => {
        if (character) {
          character.classList.remove('look-at-input', 'hide-eyes');
        }
      });
    });
  });
  