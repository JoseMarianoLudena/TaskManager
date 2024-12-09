import { Component,Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common'; // Import CommonModule

@Component({
  selector: 'app-task-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './task-list.component.html',
  styleUrl: './task-list.component.css'
})
export class TaskListComponent {
  @Input() tasks: string[] = [];
  @Output() taskDeleted = new EventEmitter<string>();

  onDelete(task: string) {
    this.taskDeleted.emit(task);
  }   
}
