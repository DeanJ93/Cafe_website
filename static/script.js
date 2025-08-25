function showEditReviewForm(reviewId) {
    const form = document.getElementById(`review-form-${reviewId}`);
    if (form) {
        form.classList.toggle("d-none");
    }
}