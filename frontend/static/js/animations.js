document.addEventListener('DOMContentLoaded', () => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.16 });

  document.querySelectorAll('.reveal').forEach((element) => observer.observe(element));

  const scrollTop = document.querySelector('.scroll-top');
  if (scrollTop) {
    window.addEventListener('scroll', () => {
      scrollTop.classList.toggle('visible', window.scrollY > 480);
    });
  }

  document.querySelectorAll('[data-counter]').forEach((counter) => {
    const target = Number(counter.dataset.counter || 0);
    const suffix = counter.dataset.suffix || '';
    const duration = 950;
    const stepTime = 16;
    const steps = Math.ceil(duration / stepTime);
    let current = 0;

    const update = () => {
      current += target / steps;
      if (current >= target) {
        counter.textContent = `${target}${suffix}`;
        return;
      }
      counter.textContent = `${Math.round(current)}${suffix}`;
      requestAnimationFrame(update);
    };

    const observerCounter = new IntersectionObserver((entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          update();
          obs.disconnect();
        }
      });
    }, { threshold: 0.5 });

    observerCounter.observe(counter);
  });
});
