import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { TaskFormComponent } from './task-form/task-form.component'; 
import { TaskListComponent } from './task-list/task-list.component'; 


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
  standalone: true,
 imports:[TaskFormComponent,TaskListComponent] 
})
export class AppComponent {
  tasks: string[] = [];

  onTaskAdded(task: string) {
    this.tasks.push(task);
  }

  onTaskDeleted(task: string) {
    this.tasks = this.tasks.filter(t => t !== task);
  }
}
