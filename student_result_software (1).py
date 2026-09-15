
import os, json, hashlib, random, string, subprocess
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

BASE = Path(__file__).resolve().parent
USERS = BASE / "users.txt"
STUDENTS = BASE / "students.txt"
REPORTS = BASE / "reports"
REPORTS.mkdir(exist_ok=True)
TITLE = "KULU SUTAR - Student Result Management System"
DEFAULT_SUBJECTS = ["Odia", "English", "Mathematics", "Science", "Social Science"]

def load_lines(path):
    if not path.exists(): return []
    out=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try: out.append(json.loads(line))
            except: pass
    return out

def save_lines(path, rows):
    path.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in rows) + ("\n" if rows else ""), encoding="utf-8")

def sha(s): return hashlib.sha256(s.encode()).hexdigest()
def otp6(): return "".join(random.choices(string.digits, k=6))
def safe(s): return "".join(c if c.isalnum() or c in "._-" else "_" for c in s) or "report"

def calc(subjects):
    full = sum(float(x["full"]) for x in subjects)
    obtained = sum(float(x["obtained"]) for x in subjects)
    pct = obtained/full*100 if full else 0
    grade = "A+" if pct >= 90 else "A" if pct >= 75 else "B" if pct >= 60 else "C" if pct >= 45 else "D" if pct >= 33 else "F"
    result = "PASS" if pct >= 33 and all(float(x["obtained"]) >= 0 for x in subjects) else "FAIL"
    return full, obtained, pct, grade, result

class ScrollFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.canvas=tk.Canvas(self, highlightthickness=0)
        self.sb=ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner=ttk.Frame(self.canvas)
        self.win=self.canvas.create_window((0,0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.sb.set)
        self.canvas.pack(side="left", fill="both", expand=True); self.sb.pack(side="right", fill="y")
        self.inner.bind("<Configure>", lambda e:self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e:self.canvas.itemconfigure(self.win,width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda e:self.canvas.yview_scroll(int(-e.delta/120),"units"))

class Register(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master); self.title("Registration"); self.geometry("580x640"); self.resizable(False,False)
        self.otp=None
        f=ttk.Frame(self,padding=25); f.pack(fill="both",expand=True)
        ttk.Label(f,text="WELCOME KULU SUTAR",font=("Segoe UI",20,"bold")).pack(pady=(5,20))
        self.e={}
        for lab in ["User ID","Email ID","Mobile No.","Password","Confirm Password"]:
            ttk.Label(f,text=lab).pack(anchor="w",pady=(5,2))
            x=ttk.Entry(f,show="*" if "Password" in lab else ""); x.pack(fill="x"); self.e[lab]=x
        ttk.Label(f,text="For offline testing, OTP is displayed here. Real SMS/email delivery needs a provider/API.",wraplength=510).pack(pady=15)
        self.otp_lbl=ttk.Label(f,text="OTP: ------",font=("Segoe UI",18,"bold")); self.otp_lbl.pack()
        self.otp_in=ttk.Entry(f); self.otp_in.pack(fill="x",pady=10)
        ttk.Button(f,text="Generate OTP",command=self.gen).pack(fill="x",pady=4)
        ttk.Button(f,text="Register",command=self.register).pack(fill="x",pady=4)
    def gen(self):
        self.otp=otp6(); self.otp_lbl.config(text="OTP: "+self.otp)
    def register(self):
        uid=self.e["User ID"].get().strip(); email=self.e["Email ID"].get().strip(); mobile=self.e["Mobile No."].get().strip()
        pw=self.e["Password"].get(); cp=self.e["Confirm Password"].get()
        if not all([uid,email,mobile,pw,cp]): return messagebox.showerror("Registration","All fields are required.",parent=self)
        if pw!=cp: return messagebox.showerror("Registration","Passwords do not match.",parent=self)
        if not self.otp: return messagebox.showerror("Registration","Generate OTP first.",parent=self)
        if self.otp_in.get().strip()!=self.otp: return messagebox.showerror("Registration","Invalid OTP.",parent=self)
        rows=load_lines(USERS)
        if any(x["user_id"].lower()==uid.lower() for x in rows): return messagebox.showerror("Registration","User ID already exists.",parent=self)
        rows.append({"user_id":uid,"email":email,"mobile":mobile,"password":sha(pw),"created_at":datetime.now().isoformat(timespec="seconds")})
        save_lines(USERS,rows); messagebox.showinfo("Registration","Registration successful. Login now.",parent=self); self.destroy()


class ForgotPassword(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Forgot Password")
        self.geometry("580x560")
        self.resizable(False, False)
        self.otp = None
        self.user = None

        f = ttk.Frame(self, padding=25)
        f.pack(fill="both", expand=True)

        ttk.Label(f, text="RESET PASSWORD", font=("Segoe UI", 20, "bold")).pack(pady=(5, 20))

        self.fields = {}
        for label in ["User ID", "Registered Email ID", "Registered Mobile No."]:
            ttk.Label(f, text=label).pack(anchor="w", pady=(6, 2))
            e = ttk.Entry(f)
            e.pack(fill="x")
            self.fields[label] = e

        ttk.Button(f, text="Verify & Generate OTP", command=self.generate).pack(fill="x", pady=12)

        self.otp_label = ttk.Label(f, text="OTP: ------", font=("Segoe UI", 18, "bold"))
        self.otp_label.pack(pady=5)

        ttk.Label(f, text="Enter OTP").pack(anchor="w", pady=(10, 2))
        self.otp_entry = ttk.Entry(f)
        self.otp_entry.pack(fill="x")

        ttk.Label(f, text="New Password").pack(anchor="w", pady=(12, 2))
        self.new_password = ttk.Entry(f, show="*")
        self.new_password.pack(fill="x")

        ttk.Label(f, text="Confirm New Password").pack(anchor="w", pady=(8, 2))
        self.confirm_password = ttk.Entry(f, show="*")
        self.confirm_password.pack(fill="x")

        ttk.Button(f, text="RESET PASSWORD", command=self.reset).pack(fill="x", pady=15)
        ttk.Button(f, text="Close", command=self.destroy).pack(fill="x")

        ttk.Label(
            f,
            text="For offline/local testing, the OTP is displayed on this screen.",
            wraplength=500,
            justify="center"
        ).pack(pady=12)

    def generate(self):
        uid = self.fields["User ID"].get().strip()
        email = self.fields["Registered Email ID"].get().strip().lower()
        mobile = self.fields["Registered Mobile No."].get().strip()

        if not uid or not email or not mobile:
            return messagebox.showerror(
                "Forgot Password",
                "Enter User ID, Registered Email ID and Registered Mobile No.",
                parent=self
            )

        users = load_lines(USERS)
        user = next(
            (
                x for x in users
                if x.get("user_id", "").lower() == uid.lower()
                and x.get("email", "").lower() == email
                and x.get("mobile", "") == mobile
            ),
            None
        )
        if not user:
            return messagebox.showerror(
                "Forgot Password",
                "User verification failed. Check your registered details.",
                parent=self
            )

        self.user = user
        self.otp = otp6()
        self.otp_label.config(text="OTP: " + self.otp)

    def reset(self):
        if not self.user or not self.otp:
            return messagebox.showerror(
                "Forgot Password",
                "First verify your registered details and generate OTP.",
                parent=self
            )

        if self.otp_entry.get().strip() != self.otp:
            return messagebox.showerror("Forgot Password", "Invalid OTP.", parent=self)

        pw = self.new_password.get()
        cp = self.confirm_password.get()

        if len(pw) < 4:
            return messagebox.showerror(
                "Forgot Password",
                "Password should contain at least 4 characters.",
                parent=self
            )
        if pw != cp:
            return messagebox.showerror(
                "Forgot Password",
                "New Password and Confirm Password do not match.",
                parent=self
            )

        users = load_lines(USERS)
        for u in users:
            if u.get("user_id") == self.user.get("user_id"):
                u["password"] = sha(pw)
                u["updated_at"] = datetime.now().isoformat(timespec="seconds")
                break
        save_lines(USERS, users)

        messagebox.showinfo(
            "Forgot Password",
            "Password reset successfully. You can now login with the new password.",
            parent=self
        )
        self.destroy()


class Main(tk.Toplevel):
    def __init__(self, root, user):
        super().__init__(root); self.root=root; self.user=user; self.title(TITLE); self.geometry("1250x800"); self.minsize(1000,650)
        self.protocol("WM_DELETE_WINDOW",self.close)
        self.subjects=DEFAULT_SUBJECTS[:]; self.rows=[]
        self.roll=tk.StringVar(); self.search=tk.StringVar()
        top=ttk.Frame(self,padding=10); top.pack(fill="x")
        ttk.Label(top,text="WELCOME KULU SUTAR",font=("Segoe UI",22,"bold")).pack(side="left")
        ttk.Label(top,text="Logged in: "+user["user_id"]).pack(side="right")
        bar=ttk.Frame(self,padding=(10,0,10,8)); bar.pack(fill="x")
        for text,cmd in [("Subjects Add/Remove",self.subject_editor),("Save",self.save),("Clear",self.clear),("Generate PDF",self.pdf),("Print",self.print_report),("Logout",self.close)]:
            ttk.Button(bar,text=text,command=cmd).pack(side="left",padx=3)
        pan=ttk.PanedWindow(self,orient="horizontal"); pan.pack(fill="both",expand=True,padx=10,pady=5)
        left=ttk.Frame(pan); right=ttk.Frame(pan); pan.add(left,weight=3); pan.add(right,weight=2)
        sf=ScrollFrame(left); sf.pack(fill="both",expand=True); f=sf.inner
        box=ttk.LabelFrame(f,text="Student Details",padding=12); box.pack(fill="x",padx=8,pady=8)
        self.fields={}
        detail=["School Name","Class","Student Name","Father Name","Mother Name","DOB","Roll No"]
        for r,lab in enumerate(detail):
            ttk.Label(box,text=lab).grid(row=r,column=0,sticky="w",padx=5,pady=5)
            e=ttk.Entry(box); e.grid(row=r,column=1,sticky="ew",padx=5,pady=5); self.fields[lab]=e
        box.columnconfigure(1,weight=1)
        lb=ttk.Frame(f,padding=8); lb.pack(fill="x")
        ttk.Label(lb,text="Load by Roll No").pack(side="left"); ttk.Entry(lb,textvariable=self.roll,width=20).pack(side="left",padx=8); ttk.Button(lb,text="Load",command=self.load).pack(side="left")
        self.sbox=ttk.LabelFrame(f,text="Subjects - Full Mark / Obtained Mark",padding=8); self.sbox.pack(fill="x",padx=8,pady=8)
        self.build_subjects()
        cb=ttk.LabelFrame(f,text="Automatic Calculation",padding=10); cb.pack(fill="x",padx=8,pady=8)
        self.cv={x:tk.StringVar(value="0") for x in ["Total Full","Total Obtained","Percentage","Grade","Result"]}
        for i,k in enumerate(self.cv):
            ttk.Label(cb,text=k+":").grid(row=i//2,column=(i%2)*2,sticky="w",padx=5,pady=4)
            ttk.Label(cb,textvariable=self.cv[k],font=("Segoe UI",10,"bold")).grid(row=i//2,column=(i%2)*2+1,sticky="w",padx=5,pady=4)
        lf=ttk.LabelFrame(right,text="Student List",padding=8); lf.pack(fill="both",expand=True)
        s=ttk.Frame(lf); s.pack(fill="x",pady=(0,8)); ttk.Label(s,text="Search").pack(side="left"); q=ttk.Entry(s,textvariable=self.search); q.pack(side="left",fill="x",expand=True,padx=6); q.bind("<KeyRelease>",lambda e:self.refresh())
        ttk.Button(s,text="Search",command=self.refresh).pack(side="left")
        cols=("roll","name","class","pct","res"); self.tree=ttk.Treeview(lf,columns=cols,show="headings")
        for c,h,w in zip(cols,["Roll No","Student Name","Class","%","Result"],[90,180,90,80,80]):
            self.tree.heading(c,text=h); self.tree.column(c,width=w,anchor="center")
        self.tree.pack(fill="both",expand=True); self.tree.bind("<Double-1>",lambda e:self.tree_load())
        a=ttk.Frame(lf); a.pack(fill="x",pady=8); ttk.Button(a,text="Edit / Load",command=self.tree_load).pack(side="left",padx=3); ttk.Button(a,text="Delete by Roll No",command=self.delete).pack(side="left",padx=3); ttk.Button(a,text="Refresh",command=self.refresh).pack(side="left",padx=3)
        self.refresh()
    def close(self): self.destroy(); self.root.deiconify()
    def subject_editor(self):
        w=tk.Toplevel(self); w.title("Subject Add / Remove"); w.geometry("430x430")
        lb=tk.Listbox(w,height=14); lb.pack(fill="both",expand=True,padx=15,pady=15)
        for x in self.subjects: lb.insert("end",x)
        b=ttk.Frame(w,padding=10); b.pack(fill="x"); ent=ttk.Entry(b); ent.pack(side="left",fill="x",expand=True)
        def add():
            x=ent.get().strip()
            if x and x not in self.subjects: self.subjects.append(x); lb.insert("end",x); ent.delete(0,"end"); self.build_subjects()
        def rem():
            s=lb.curselection()
            if s: self.subjects.pop(s[0]); lb.delete(s[0]); self.build_subjects()
        ttk.Button(b,text="Add",command=add).pack(side="left",padx=4); ttk.Button(b,text="Remove",command=rem).pack(side="left")
        ttk.Button(w,text="Close",command=w.destroy).pack(pady=8)
    def build_subjects(self):
        for w in self.sbox.winfo_children(): w.destroy()
        self.rows=[]
        for c,h in enumerate(["Subject","Full Mark","Obtained Mark"]): ttk.Label(self.sbox,text=h,font=("Segoe UI",9,"bold")).grid(row=0,column=c,sticky="w",padx=4,pady=4)
        for r,sub in enumerate(self.subjects,1):
            ttk.Label(self.sbox,text=sub).grid(row=r,column=0,sticky="w",padx=4,pady=3)
            a=ttk.Entry(self.sbox,width=15); b=ttk.Entry(self.sbox,width=15); a.insert(0,"100"); b.insert(0,"0")
            a.grid(row=r,column=1,padx=4,pady=3); b.grid(row=r,column=2,padx=4,pady=3); a.bind("<KeyRelease>",lambda e:self.update()); b.bind("<KeyRelease>",lambda e:self.update())
            self.rows.append((sub,a,b))
        self.update()
    def update(self):
        ss=[]
        for n,a,b in self.rows:
            try: f=float(a.get() or 0); o=float(b.get() or 0)
            except: f=o=0
            ss.append({"name":n,"full":f,"obtained":o})
        f,o,p,g,r=calc(ss); self.cv["Total Full"].set(f"{f:g}"); self.cv["Total Obtained"].set(f"{o:g}"); self.cv["Percentage"].set(f"{p:.2f}%"); self.cv["Grade"].set(g); self.cv["Result"].set(r)
    def form(self):
        d={k:e.get().strip() for k,e in self.fields.items()}
        if not all(d.values()): raise ValueError("Please fill all student fields.")
        ss=[]
        for n,a,b in self.rows:
            try: f=float(a.get()); o=float(b.get())
            except: raise ValueError("Invalid marks for "+n)
            if f<=0 or o<0 or o>f: raise ValueError("Invalid marks for "+n)
            ss.append({"name":n,"full":f,"obtained":o})
        f,o,p,g,r=calc(ss); d.update(subjects=ss,total_full=f,total_obtained=o,percentage=p,grade=g,result=r,updated_at=datetime.now().isoformat(timespec="seconds")); return d
    def save(self):
        try: st=self.form()
        except ValueError as e: return messagebox.showerror("Save",str(e),parent=self)
        rows=load_lines(STUDENTS); rows=[x for x in rows if str(x.get("Roll No","")).lower()!=st["Roll No"].lower()]; rows.append(st); save_lines(STUDENTS,rows); self.refresh(); self.roll.set(st["Roll No"]); messagebox.showinfo("Save","Student saved/updated successfully.",parent=self)
    def clear(self):
        for e in self.fields.values(): e.delete(0,"end")
        self.roll.set(""); self.build_subjects()
    def load(self):
        roll=self.roll.get().strip()
        st=next((x for x in load_lines(STUDENTS) if str(x.get("Roll No","")).lower()==roll.lower()),None)
        if not st: return messagebox.showerror("Load","Student not found.",parent=self)
        for k,e in self.fields.items(): e.delete(0,"end"); e.insert(0,st.get(k,""))
        self.subjects=[x["name"] for x in st.get("subjects",[])] or DEFAULT_SUBJECTS[:]; self.build_subjects()
        mp={x["name"]:x for x in st.get("subjects",[])}
        for n,a,b in self.rows:
            if n in mp: a.delete(0,"end"); a.insert(0,str(mp[n]["full"])); b.delete(0,"end"); b.insert(0,str(mp[n]["obtained"]))
        self.update()
    def refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        q=self.search.get().strip().lower()
        for s in load_lines(STUDENTS):
            txt=" ".join(str(s.get(k,"")) for k in ["Roll No","Student Name","Class","School Name"]).lower()
            if q and q not in txt: continue
            self.tree.insert("","end",values=(s.get("Roll No",""),s.get("Student Name",""),s.get("Class",""),f"{float(s.get('percentage',0)):.2f}",s.get("result","")))
    def tree_load(self):
        s=self.tree.selection()
        if s: self.roll.set(self.tree.item(s[0],"values")[0]); self.load()
    def delete(self):
        roll=self.roll.get().strip()
        if not roll:
            s=self.tree.selection()
            if s: roll=self.tree.item(s[0],"values")[0]
        if not roll: return messagebox.showerror("Delete","Enter/select Roll No.",parent=self)
        if not messagebox.askyesno("Delete","Delete Roll No "+roll+"?",parent=self): return
        rows=load_lines(STUDENTS); new=[x for x in rows if str(x.get("Roll No","")).lower()!=roll.lower()]
        if len(new)==len(rows): return messagebox.showerror("Delete","Student not found.",parent=self)
        save_lines(STUDENTS,new); self.clear(); self.refresh(); messagebox.showinfo("Delete","Student deleted.",parent=self)
    def current(self):
        try: return self.form()
        except:
            roll=self.roll.get().strip()
            st=next((x for x in load_lines(STUDENTS) if str(x.get("Roll No","")).lower()==roll.lower()),None)
            if st: return st
            raise ValueError("Enter valid student data or load by Roll No.")
    def pdf_file(self, st):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Paragraph,Spacer
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet
        except ImportError: raise RuntimeError("ReportLab missing. Run: python -m pip install reportlab")
        path=REPORTS/(safe(st["Student Name"])+"_"+safe(st["Roll No"])+".pdf")
        doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=30,leftMargin=30,topMargin=30,bottomMargin=30); sty=getSampleStyleSheet(); story=[Paragraph("KULU SUTAR - STUDENT RESULT REPORT",sty["Title"]),Spacer(1,12)]
        info=[["School Name",st["School Name"],"Class",st["Class"]],["Student Name",st["Student Name"],"Roll No",st["Roll No"]],["Father Name",st["Father Name"],"Mother Name",st["Mother Name"]],["DOB",st["DOB"],"", ""]]
        t=Table(info,colWidths=[90,190,75,150]); t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.5,colors.black),("BACKGROUND",(0,0),(0,-1),colors.lightgrey),("BACKGROUND",(2,0),(2,-1),colors.lightgrey)])); story += [t,Spacer(1,15)]
        data=[["Subject","Full Mark","Obtained Mark"]]+[[x["name"],f'{float(x["full"]):g}',f'{float(x["obtained"]):g}'] for x in st["subjects"]]+[["Total",f'{float(st["total_full"]):g}',f'{float(st["total_obtained"]):g}'],["Percentage","",f'{float(st["percentage"]):.2f}%'],["Grade","",st["grade"]],["Result","",st["result"]]]
        mt=Table(data,colWidths=[270,110,125]); mt.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.5,colors.black),("BACKGROUND",(0,0),(-1,0),colors.lightgrey),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTNAME",(0,-4),(-1,-1),"Helvetica-Bold")])); story += [mt,Spacer(1,20),Paragraph("Generated: "+datetime.now().strftime("%d-%m-%Y %I:%M %p"),sty["Normal"])]
        doc.build(story); return path
    def pdf(self):
        try:
            p=self.pdf_file(self.current()); messagebox.showinfo("PDF","PDF created:\n"+str(p),parent=self); os.startfile(str(p))
        except Exception as e: messagebox.showerror("PDF",str(e),parent=self)
    def print_report(self):
        try:
            p=self.pdf_file(self.current())
            try: os.startfile(str(p),"print")
            except: subprocess.Popen(["explorer",str(p)])
        except Exception as e: messagebox.showerror("Print",str(e),parent=self)

class Login(tk.Tk):
    def __init__(self):
        super().__init__(); self.title(TITLE); self.geometry("520x410"); self.resizable(False,False)
        ttk.Label(self,text="WELCOME KULU SUTAR",font=("Segoe UI",24,"bold")).pack(pady=(25,8))
        ttk.Label(self,text="Student Result Management System",font=("Segoe UI",11)).pack(pady=(0,25))
        f=ttk.Frame(self,padding=10); f.pack(fill="x")
        ttk.Label(f,text="User ID").grid(row=0,column=0,sticky="w",pady=8); self.uid=ttk.Entry(f); self.uid.grid(row=0,column=1,sticky="ew",pady=8)
        ttk.Label(f,text="Password").grid(row=1,column=0,sticky="w",pady=8); self.pw=ttk.Entry(f,show="*"); self.pw.grid(row=1,column=1,sticky="ew",pady=8); f.columnconfigure(1,weight=1)
        ttk.Button(self,text="LOGIN",command=self.login).pack(fill="x",padx=35,pady=8); ttk.Button(self,text="NEW REGISTRATION",command=lambda:Register(self)).pack(fill="x",padx=35,pady=8)
        ttk.Button(self,text="FORGOT PASSWORD?",command=lambda:ForgotPassword(self)).pack(fill="x",padx=35,pady=8)
        ttk.Button(self,text="EXIT",command=self.destroy).pack(fill="x",padx=35,pady=8)
    def login(self):
        uid=self.uid.get().strip(); pw=self.pw.get()
        u=next((x for x in load_lines(USERS) if x["user_id"].lower()==uid.lower()),None)
        if not u or u["password"]!=sha(pw): return messagebox.showerror("Login","Invalid User ID or Password.",parent=self)
        self.withdraw(); Main(self,u)

if __name__=="__main__": Login().mainloop()
