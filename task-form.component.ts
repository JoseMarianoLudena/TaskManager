import { Component,EventEmitter,Output  } from '@angular/core';
import { FormsModule } from '@angular/forms'; // Import FormsModule
@Component({
  selector: 'app-task-form',
  standalone: true,
  templateUrl: './task-form.component.html',
  styleUrl: './task-form.component.css',
  imports: [FormsModule],
})
export class TaskFormComponent {
  task: string = '';
  @Output() taskAdded = new EventEmitter<string>();

  onSubmit() {
    this.taskAdded.emit(this.task);
    this.task = '';
  }
}
