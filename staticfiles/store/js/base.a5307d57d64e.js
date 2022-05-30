window.addEventListener('DOMContentLoaded', () => {
  var menuDrop = document.getElementById('menu-dropdown');
  var menuItems= document.getElementById('menu-items');
  
  menuDrop.addEventListener('click', () => {
    menuItems.classList.toggle('hidden')
  })
})