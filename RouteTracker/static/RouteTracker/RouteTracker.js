$(function () {
    $('[data-toggle="tooltip"]').tooltip()
  })

  
  const nav = document.querySelector('.mainNavbar');
  const header = document.querySelector('.js-nav');
  const navHeight = nav.getBoundingClientRect().height;

  const stickyNav = function (entries){
    const [entry] = entries;
    if (!entry.isIntersecting) {
      nav.classList.add('sticky');
    } 
    else{
      nav.classList.remove('sticky');
    } 
  };

  const headerObserver = new IntersectionObserver(
    stickyNav,{
      root:null,
      threshold: 0, // percentage we want visible in the view port with the current target 
      rootMargin: '50px'
    }
  );
  headerObserver.observe(header); 

