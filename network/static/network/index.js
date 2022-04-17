document.addEventListener('DOMContentLoaded', function () {
	const posts = document.querySelectorAll('.post');
	posts.forEach((p) => {
		const content = p.querySelector('.content');
		const editButton = p.querySelector('.edit');
		const like = p.querySelector('.like');
		if (editButton) {
			editButton.addEventListener('click', function () {
				if (editButton.innerHTML.trim() == 'Edit') {
					editButton.innerHTML = 'Save';
					content.innerHTML =
						'<textarea id="content-textarea" rows="6" cols="50" class="my-2">' +
						content.innerHTML +
						'</textarea>';
				} else {
					editButton.innerHTML = 'Edit';
					fetch('/edit/' + editButton.dataset.id, {
						method: 'POST',
						body: JSON.stringify({
							content: document.querySelector('#content-textarea').value,
						}),
					})
						.then((response) => response.json())
						.then((data) => {
							console.log(data);
							if (data.success) {
								content.innerHTML = data.content;
							} else {
								alert('Error: ' + data.error);
							}
						});

					content.innerHTML = document.querySelector('#content-textarea').value;
				}
			});
		}
		like.addEventListener('click', function () {
			fetch('/like/' + like.dataset.id, {
				method: 'POST',
			})
				.then((response) => response.json())
				.then((data) => {
					console.log(data);
					if (data.success) {
						like.innerHTML = data.action === 'like' ? 'Like' : 'Unlike';
						p.querySelector('.likesCount').innerHTML = data.likes;
					} else {
						alert('Error: ' + data.error);
					}
				});
		});
	});
});
