import flet as ft

class GradeCalculator:
    """Main Grade Calculator application built with Flet v0.28."""

    def __init__(self, page: ft.Page):
        self.page = page
        
        self.name_input = ft.TextField(
            hint_text="Enter student name",
            bgcolor=ft.Colors.WHITE,
            width=650,
            on_submit=self.add_grade_from_event,
        )
        
        self.subject_dropdown = ft.Dropdown(
            hint_text="Select subject",
            bgcolor=ft.Colors.WHITE,
            width=650,
            options=[
                ft.dropdown.Option(key="Math", text="Math"),
                ft.dropdown.Option(key="Science", text="Science"),
                ft.dropdown.Option(key="English", text="English"),
                ft.dropdown.Option(key="History", text="History"),
                ft.dropdown.Option(key="Computer Science", text="Computer Science"),
            ],
        )
        
        self.grade_input = ft.TextField(
            hint_text="Enter grade (0-100)",
            bgcolor=ft.Colors.WHITE,
            width=650,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_submit=self.add_grade_from_event,
        )
        
        self.add_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=ft.Colors.BLUE,
            width=650,
            on_click=self.add_grade_clicked,
        )
        
        self.stats_text = ft.Text(
            "No grades recorded",
            color=ft.Colors.GREY_700,
            size=16,
            weight=ft.FontWeight.BOLD,
        )
        
        self.stats_bar = ft.ProgressBar(
            width=650,
            value=0,
            color=ft.Colors.GREEN,
        )
        
        self.grades_list = ft.Column(spacing=10)
        
        self.view = ft.Column(
            width=650,
            spacing=25,
            controls=[
                ft.Column(
                    spacing=10,
                    controls=[
                        self.name_input,
                        self.subject_dropdown,
                        self.grade_input,
                        self.add_button,
                    ],
                ),
                ft.Column(
                    spacing=8,
                    controls=[self.stats_text, self.stats_bar],
                ),
                self.grades_list,
            ],
        )

    def add_grade_from_event(self, e: ft.ControlEvent):
        """Handle Enter key press in input fields."""
        self.add_grade()

    def add_grade_clicked(self, e: ft.ControlEvent):
        """Handle Add button click."""
        self.add_grade()

    def add_grade(self):
        """Core logic to validate and add a new grade."""
        student_name = (self.name_input.value or "").strip()
        subject = self.subject_dropdown.value
        grade_str = (self.grade_input.value or "").strip()
        
        if not student_name:
            self.show_error("Please enter a student name.")
            return
        
        if not subject:
            self.show_error("Please select a subject.")
            return
        
        try:
            grade = float(grade_str)
            if grade < 0 or grade > 100:
                self.show_error("Please enter a valid grade between 0 and 100.")
                return
        except (ValueError, TypeError):
            self.show_error("Please enter a valid grade between 0 and 100.")
            return
        
        grade_row = self.create_grade_row(student_name, subject, grade)
        self.grades_list.controls.append(grade_row)
        
        self.name_input.value = ""
        self.subject_dropdown.value = ""
        self.grade_input.value = ""
        
        self.name_input.focus()
        
        self.update_statistics()
        
        self.page.update()

    def create_grade_row(self, student_name: str, subject: str, grade: float) -> ft.Row:
        """Create and configure a grade row with all its components."""
        if grade >= 90:
            bg_color = ft.Colors.BLUE_100
        elif grade >= 75:
            bg_color = ft.Colors.GREEN_100
        elif grade >= 60:
            bg_color = ft.Colors.ORANGE_100
        else:
            bg_color = ft.Colors.RED_100
        
        grade_text = ft.Text(f"{subject} - {student_name}: {grade}")
        
        grade_container = ft.Container(
            content=grade_text,
            bgcolor=bg_color,
            padding=ft.padding.symmetric(horizontal=8, vertical=6),
            border_radius=ft.border_radius.all(6),
            expand=True,
        )
        
        delete_button = ft.IconButton(
            icon=ft.Icons.DELETE,
            icon_color=ft.Colors.RED,
            bgcolor=ft.Colors.RED_50,
            tooltip="Delete Grade",
        )
        
        def delete_clicked(_: ft.ControlEvent):
            def confirm_delete(_):
                self.page.close(delete_dialog)
                if grade_row in self.grades_list.controls:
                    self.grades_list.controls.remove(grade_row)
                    self.grades_list.update()
                    self.update_statistics()
            
            def cancel_delete(_):
                self.page.close(delete_dialog)
            
            delete_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirm Deletion"),
                content=ft.Text(
                    f"Are you sure you want to delete this grade entry?\n\n"
                    f"{subject} - {student_name}: {grade}"
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=cancel_delete),
                    ft.TextButton("Delete", on_click=confirm_delete),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.open(delete_dialog)
        
        delete_button.on_click = delete_clicked
        
        # Create grade row
        grade_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[grade_container, delete_button],
        )
        
        grade_row.data = grade
        
        return grade_row

    def update_statistics(self):
        """Recalculate and update statistics bar and text."""
        total_grades = len(self.grades_list.controls)
        
        if total_grades == 0:
            self.stats_bar.value = 0
            self.stats_text.value = "No grades recorded"
            self.stats_bar.color = ft.Colors.GREEN
        else:
            grades = [row.data for row in self.grades_list.controls]
            
            average = sum(grades) / len(grades)
            highest = max(grades)
            lowest = min(grades)
            
            self.stats_text.value = (
                f"Total Grades: {total_grades} | Average: {average:.1f} | "
                f"Highest: {int(highest)} | Lowest: {int(lowest)}"
            )
            
            self.stats_bar.value = average / 100
            
            if average >= 75:
                self.stats_bar.color = ft.Colors.GREEN
            elif average >= 60:
                self.stats_bar.color = ft.Colors.ORANGE
            else:
                self.stats_bar.color = ft.Colors.RED
        
        self.stats_bar.update()
        self.stats_text.update()

    def show_error(self, message: str):
        """Display error dialog with given message."""
        def close_dialog(_):
            self.page.close(error_dialog)
        
        error_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Invalid Input"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        self.page.open(error_dialog)


def main(page: ft.Page):
    """Configure page and launch the Grade Calculator application."""
    page.title = "Albano Grade Calculator"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.bgcolor = ft.Colors.PURPLE_50
    page.window.width = 450
    page.window.height = 750
    page.window.center()
    page.window.resizable = False
    page.scroll = "auto"
    
    app = GradeCalculator(page)
    page.add(app.view)


if '_name_' == "_main_":
    ft.app(target=main)