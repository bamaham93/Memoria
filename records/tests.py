from datetime import datetime

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Document, Category


class AuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_redirect_if_not_logged_in(self):
        """Unauthenticated users should be redirected to /login/"""
        response = self.client.get(reverse("document_list"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('document_list')}")

    def test_logged_in_can_access_docs(self):
        """Logged in users should see the documents page"""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("document_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Available Documents")


class DocumentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        # Create documents across different years and months
        self.doc1 = Document.objects.create(
            title="Doc 2023 Jan",
            description="Old doc",
            file=SimpleUploadedFile("doc1.pdf", b"PDF content"),
            uploaded_at=timezone.make_aware(datetime(2023, 1, 10))
        )
        self.doc2 = Document.objects.create(
            title="Doc 2024 Mar",
            description="Mid doc",
            file=SimpleUploadedFile("doc2.pdf", b"PDF content"),
            uploaded_at=timezone.make_aware(datetime(2024, 3, 5))
        )
        self.doc3 = Document.objects.create(
            title="Doc 2024 Dec",
            description="Recent doc",
            file=SimpleUploadedFile("doc3.pdf", b"PDF content"),
            uploaded_at=timezone.make_aware(datetime(2024, 12, 20))
        )

    def test_document_display(self):
        """Uploaded documents appear in the list"""
        response = self.client.get(reverse("document_list"))
        self.assertContains(response, "Doc 2023 Jan")
        self.assertContains(response, "Doc 2024 Mar")
        self.assertContains(response, "Doc 2024 Dec")

    def test_filter_by_year(self):
        """Filtering by year only shows docs from that year"""
        response = self.client.get(reverse("document_list"), {"year": "2023"})
        self.assertContains(response, "Doc 2023 Jan")
        self.assertNotContains(response, "Doc 2024 Mar")
        self.assertNotContains(response, "Doc 2024 Dec")

    def test_filter_by_month(self):
        """Filtering by month only shows docs from that month"""
        response = self.client.get(reverse("document_list"), {"month": "03"})
        self.assertContains(response, "Doc 2024 Mar")
        self.assertNotContains(response, "Doc 2023 Jan")
        self.assertNotContains(response, "Doc 2024 Dec")

    def test_filter_by_year_and_month(self):
        """Filtering by year + month narrows results correctly"""
        response = self.client.get(reverse("document_list"), {"year": "2024", "month": "12"})
        self.assertContains(response, "Doc 2024 Dec")
        self.assertNotContains(response, "Doc 2024 Mar")
        self.assertNotContains(response, "Doc 2023 Jan")

    def test_sort_oldest_first(self):
        """Sort=asc shows oldest doc first"""
        response = self.client.get(reverse("document_list"), {"sort": "asc"})
        content = response.content.decode()
        self.assertTrue(content.index("Doc 2023 Jan") < content.index("Doc 2024 Mar") < content.index("Doc 2024 Dec"))

    def test_sort_newest_first(self):
        """Sort=desc shows newest doc first"""
        response = self.client.get(reverse("document_list"), {"sort": "desc"})
        content = response.content.decode()
        self.assertTrue(content.index("Doc 2024 Dec") < content.index("Doc 2024 Mar") < content.index("Doc 2023 Jan"))


class CategoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        self.category = Category.objects.create(name="Business Meeting Minutes")
        self.doc = Document.objects.create(
            title="Business Meeting Doc",
            description="Minutes from the meeting",
            category=self.category,
            file=SimpleUploadedFile("doc.pdf", b"PDF content"),
            uploaded_at=timezone.now()
        )

    def test_category_badge_displayed(self):
        """Category badge should show in document list"""
        response = self.client.get(reverse("document_list"))
        self.assertContains(response, "Business Meeting Doc")
        self.assertContains(response, "Business Meeting Minutes")  # Category name


class SignupLoginLogoutTests(TestCase):
    def test_signup_creates_user_and_redirects(self):
        """Signup should create a new user and log them in"""
        response = self.client.post(reverse("signup"), {
            "username": "newuser",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        })
        # After signup, redirect to home
        self.assertRedirects(response, reverse("document_list"))
        # User should exist
        self.assertTrue(User.objects.filter(username="newuser").exists())
        # User should be logged in
        response = self.client.get(reverse("document_list"))
        self.assertEqual(str(response.context["user"]), "newuser")

    def test_login_with_valid_credentials(self):
        """Login should succeed with correct credentials"""
        User.objects.create_user(username="testuser", password="testpass")
        response = self.client.post(reverse("login"), {
            "username": "testuser",
            "password": "testpass",
        })
        self.assertRedirects(response, reverse("document_list"))
        # Confirm logged in
        response = self.client.get(reverse("document_list"))
        self.assertTrue(response.context["user"].is_authenticated)

    def test_login_with_invalid_credentials_fails(self):
        """Login should fail with wrong password"""
        User.objects.create_user(username="testuser", password="testpass")
        response = self.client.post(reverse("login"), {
            "username": "testuser",
            "password": "wrongpass",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password")  # Django default error

    def test_logout_clears_session(self):
        """Logout should log the user out and redirect to login"""
        User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
        # Confirm user is logged out
        response = self.client.get(reverse("document_list"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('document_list')}")

    def test_invalid_signup_shows_errors(self):
        """Invalid signup should re-render the form with errors and not create a user"""
        response = self.client.post(reverse("signup"), {
            "username": "baduser",
            "password1": "abc12345",
            "password2": "different12345",  # mismatched
        })

        # Page should not redirect, should re-render with status 200
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The two password fields didn’t match.")  # Django default error
        # User should not exist
        self.assertFalse(User.objects.filter(username="baduser").exists())

    def test_signup_template_contains_fields(self):
        """Signup form should contain username, password1, and password2 fields"""
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)

        # Check for input fields in the HTML
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password1"')
        self.assertContains(response, 'name="password2"')

    def test_login_template_contains_fields(self):
        """Login form should contain username and password fields"""
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

        # Check for input fields in the HTML
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
