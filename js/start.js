const speakerModeElements = document.querySelectorAll('.activate-speaker-mode');
speakerModeElements.forEach(function (element) {
  element.addEventListener('click', function (event) {
    Reveal.getPlugin("notes").open();
    event.preventDefault();
  });
});

const nextSlideElements = document.querySelectorAll('.go-to-next-slide');
nextSlideElements.forEach(function (element) {
  element.addEventListener('click', function (event) {
    Reveal.next();
    event.preventDefault();
  });
});

const showShortcutsElements = document.querySelectorAll('.show-shortcuts');
showShortcutsElements.forEach(function (element) {
  element.addEventListener('click', function (event) {
    Reveal.toggleHelp();
    event.preventDefault();
  });
});

const showSearchElements = document.querySelectorAll('.show-search');
showSearchElements.forEach(function (element) {
  element.addEventListener('click', function (event) {
    Reveal.getPlugin("search").open();
    event.preventDefault();
  });
});
