const buttons = document.querySelectorAll(".amt-val");

buttons.forEach(button => {
    button.addEventListener('click', function handleClick(event) {
    const amount = document.querySelector("#amount");
    //const prevClick = document.querySelector(".ring-2")
    // clear previous formatting

    amount.value = Number(button.innerHTML)
    //button.setAttribute('class', 'ring-2 ring-indigo-500')
    });
});
