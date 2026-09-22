from django.db import models


class SchoolClass(models.Model):
    """e.g. 'Class 10', 'B.Com II'"""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Classes'

    def __str__(self):
        return self.name


class Section(models.Model):
    """e.g. Section A of Class 10"""
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=10)  # A, B, C ...

    class Meta:
        unique_together = ('school_class', 'name')
        ordering = ['school_class__name', 'name']

    def __str__(self):
        return f"{self.school_class.name} - {self.name}"


class Subject(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, blank=True)

    class Meta:
        unique_together = ('school_class', 'name')
        ordering = ['school_class__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.school_class.name})"


class Chapter(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='chapters')
    name = models.CharField(max_length=200)
    sequence = models.PositiveIntegerField(default=1, help_text="Order of the chapter in the syllabus.")

    class Meta:
        ordering = ['subject', 'sequence']

    def __str__(self):
        return f"{self.name} ({self.subject.name})"
