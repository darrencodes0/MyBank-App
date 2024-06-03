function transfer_confirmation() {
  const amount = document.getElementById("amount").value;
  const username = document.getElementById("username").value;
  const confirmation = confirm("Are you sure you want to transfer $" + amount + " to " + username + "?");
  return confirmation;
}