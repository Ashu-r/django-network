document.addEventListener('DOMContentLoaded', function () {
	document.querySelector('#follow').addEventListener('click', (e) => {
		let action = 'follow';
		if (e.target.innerHTML.trim().toLowerCase() === 'follow') {
			action = 'unfollow';
		}
		fetch('/network/follow', {
			method: 'POST',
			body: JSON.stringify({ action }),
		})
			.then((response) => response.json())
			.then((result) => {
				console.log(result);
			});
	});
});
