import tkinter as tk
from tkinter import messagebox, simpledialog, Listbox, StringVar, END
from cassandra.cluster import Cluster
import time

from utils import *


class CinemaDatabaseApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Cinema Database")
        self.master.geometry("800x800")

        self.keyspace = 'cinema'
        self.clstr = Cluster()
        self.session = self.clstr.connect(self.keyspace)

        self.user = StringVar()

        self.create_widgets()
        self.login_to_database()

    def create_widgets(self):
        self.title_label = tk.Label(self.master, text="Cinema Database", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        self.options_frame = tk.Frame(self.master)
        self.options_frame.pack(pady=10)

        self.add_btn = tk.Button(self.options_frame, text="Add reservation", command=self.add_reservation)
        self.add_btn.grid(row=0, column=0, padx=10, pady=5)

        self.show_all_btn = tk.Button(self.options_frame, text="Show your reservations", command=self.show_reservations)
        self.show_all_btn.grid(row=1, column=0, padx=10, pady=5)

        self.show_one_btn = tk.Button(self.options_frame, text="Show specific reservation", command=self.show_reservation)
        self.show_one_btn.grid(row=2, column=0, padx=10, pady=5)

        self.show_all_users_btn = tk.Button(self.options_frame, text="Show all reservations", command=self.show_all_reservations)
        self.show_all_users_btn.grid(row=3, column=0, padx=10, pady=5)

        self.update_btn = tk.Button(self.options_frame, text="Update reservation", command=self.update_reservation)
        self.update_btn.grid(row=4, column=0, padx=10, pady=5)

        self.delete_btn = tk.Button(self.options_frame, text="Cancel reservation", command=self.delete_reservation)
        self.delete_btn.grid(row=5, column=0, padx=10, pady=5)

        self.quit_btn = tk.Button(self.master, text="Quit", command=self.quit_application)
        self.quit_btn.pack(pady=10)

        self.result_listbox = Listbox(self.master, width=80, height=10)
        self.result_listbox.pack(pady=10)

    def login_to_database(self):
        self.user.set(simpledialog.askstring("Login", "Provide your unique username:"))
        if not self.user.get():
            self.master.destroy()

    def add_reservation(self):
        movie_name, seat = self.get_new_reservation_details()
        if movie_name and seat:
            try:
                add_reservation(self.user.get(), self.session, movie_name, seat)
                time.sleep(1)
                messagebox.showinfo("Success", "Successfully added your reservation!")
            except Exception as e:
                messagebox.showerror("Error", f"Exception: {e}")

    def show_reservations(self):
        self.result_listbox.delete(0, END)
        rows = get_all_reservations(self.user.get(), self.session)
        if not rows:
            messagebox.showinfo("Info", "You don't have any reservations yet.")
        else:
            self.result_listbox.insert(END, "Reservation ID, Movie name, Seat")
            for row in rows:
                self.result_listbox.insert(END, f'{row.reservation_id}, {row.movie_name}, {row.seat_number}')

    def show_reservation(self):
        row = self.get_one_reservation()
        if row:
            self.result_listbox.delete(0, END)
            self.result_listbox.insert(END, "Movie name, Seat, Reservation timestamp")
            self.result_listbox.insert(END, f'{row.movie_name}, {row.seat_number}, {row.reservation_timestamp}')

    def show_all_reservations(self):
        query = "SELECT * FROM cinema.reservations;"
        rows = self.session.execute(query)
        
        if not rows:
            messagebox.showinfo("Info", "No reservations found.")
            return

        self.result_listbox.delete(0, END)
        self.result_listbox.insert(END, "User, Reservation ID, Movie name, Seat, Reservation timestamp")
        for row in rows:
            self.result_listbox.insert(END, f'{row.name}, {row.reservation_id}, {row.movie_name}, {row.seat_number}, {row.reservation_timestamp}')


    def update_reservation(self):
        res_id, movie_name, current_seat = self.get_existent_reservation_details()
        if res_id and movie_name and current_seat:
            new_seat = self.select_seat(movie_name)
            if new_seat:
                update_reservation(self.user.get(), self.session, res_id, movie_name, current_seat, new_seat)
                time.sleep(1)
                messagebox.showinfo("Success", "Successfully updated your reservation!")

    def delete_reservation(self):
        if messagebox.askyesno("Warning", "It can't be undone. The cancellation is irreversible. Do you want to continue?"):
            res_id, movie_name, seat = self.get_existent_reservation_details()
            if res_id and movie_name and seat:
                delete_reservation(self.user.get(), self.session, res_id, movie_name, seat)
                time.sleep(1)
                messagebox.showinfo("Success", "Successfully cancelled your reservation!")

    def quit_application(self):
        self.session.shutdown()
        self.master.quit()

    def show_movies(self):
        rows = get_all_movies(self.session)
        movies = [f'{row.movie_name}, {row.show_timestamp}' for row in rows]
        return rows, movies

    def select_seat(self, movie_name):
        free_seats = avaiable_seats(self.session, movie_name)
        if not free_seats:
            messagebox.showwarning("No Seats", "There are no more free seats. Please, select another movie.")
            return None

        seat = simpledialog.askinteger("Select Seat", f"Currently available seats: {free_seats}\nPick a seat number:")
        if seat in free_seats:
            return seat
        else:
            messagebox.showerror("Invalid Seat", "Please select an available seat.")
            return self.select_seat(movie_name)

    def get_new_reservation_details(self):
        rows, movies = self.show_movies()
        movie_names = [row.movie_name for row in rows]

        movie_name = simpledialog.askstring("Select Movie", f"Available movies:\n" + '\n'.join(movie_names) + "\nMovie name:")
        if movie_name not in movie_names:
            messagebox.showerror("Error", "Wrong movie title was provided. Please try again.")
            return self.get_new_reservation_details()

        seat = self.select_seat(movie_name)
        return movie_name, seat

    def get_one_reservation(self):
        all_reservations = get_all_reservations(self.user.get(), self.session)
        if not all_reservations:
            messagebox.showinfo("Info", "You don't have any reservations yet.")
            return None

        res_id, movie_name, seat = self.get_existent_reservation_details()
        if res_id and movie_name and seat:
            query = f"SELECT * FROM cinema.reservations WHERE name = '{self.user.get()}' and reservation_id = {res_id};"
            return self.session.execute(query).one()
        else:
            messagebox.showerror("Error", "Wrong reservation id was provided. Please try again.")
            return self.get_one_reservation()

    def select_reservation(self):
        dialog = tk.Toplevel()
        dialog.title("Select Reservation")

        label = tk.Label(dialog, text="Select a reservation from the list below:")
        label.pack(pady=5)

        listbox = Listbox(dialog, width=50, height=10)
        listbox.pack(pady=5, padx=10, fill='x')

        all_reservations = get_all_reservations(self.user.get(), self.session)
        if not all_reservations:
            messagebox.showinfo("Info", "You don't have any reservations yet.")
            dialog.destroy()
            return None, None, None

        reservation_map = {}
        for row in all_reservations:
            reservation_id = str(row.reservation_id)
            reservation_map[reservation_id] = (row.movie_name, int(row.seat_number))
            listbox.insert(END, f'ID: {reservation_id}, Movie: {row.movie_name}, Seat: {row.seat_number}')

        selected_reservation_id = StringVar()

        def on_select():
            selection = listbox.curselection()
            if selection:
                selected_id = listbox.get(selection[0]).split(',')[0].split(': ')[1]
                selected_reservation_id.set(selected_id)
                dialog.destroy()
            else:
                messagebox.showwarning("Warning", "Please select a reservation from the list.")

        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=5)

        select_button = tk.Button(button_frame, text="Select", command=on_select)
        select_button.pack(side=tk.LEFT, padx=5)

        dialog.transient()
        dialog.grab_set()
        dialog.wait_window()

        selected_id = selected_reservation_id.get()
        if selected_id:
            movie_name, seat = reservation_map[selected_id]
            return selected_id, movie_name, seat
        return None, None, None

    def get_existent_reservation_details(self):
        res_id, movie_name, seat = self.select_reservation()
        if res_id and movie_name and seat:
            return res_id, movie_name, seat
        else:
            messagebox.showinfo("Info", "No reservation selected.")
            return None, None, None


if __name__ == "__main__":
    root = tk.Tk()
    app = CinemaDatabaseApp(root)
    root.mainloop()
