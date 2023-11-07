import json
# khởi tạo các class
class Employee:
    def __init__(self, id, name, salary_base, working_days, department, working_performance, bonus, late_coming_days):
        self.id = id
        self.name = name
        self.salary_base = salary_base
        self.working_days = working_days
        self.department = department
        self.working_performance = working_performance
        self.bonus = bonus
        self.late_coming_days = late_coming_days

    def calculate_salary(self, department_dict, tax_dict, phat_dict):
        total_income = (self.salary_base * self.working_days) * self.working_performance
        # lấy giá trị thưởng bộ phận tương ứng nếu id bộ phận của nhân viên có trong dict {bộ phận : thưởng bp}
        department_bonus = department_dict.get(self.department, 0)
        # kiểm tra xem đối tượng employee có thuộc class manager không, nếu thuộc manager thì nhận hệ số thưởng 10%
        if isinstance(self, Manager):
            department_bonus = department_bonus * 1.1

        total_bonus = self.bonus + department_bonus
        total_penalty =  calculate_late(self.late_coming_days,phat_dict)
        taxable_income = (total_income + total_bonus - total_penalty) * 89.5 /100
        income_tax = calculate_income_tax(taxable_income, tax_dict)

        net_salary = taxable_income - income_tax
        return int(net_salary)
class Manager(Employee):
    def __init__(self, id, name, salary_base, working_days, department, working_performance, bonus, late_coming_days):
        super().__init__(id, name, salary_base, working_days, department, working_performance, bonus, late_coming_days)
class Department:
    def __init__(self, id, bonus_salary):
        self.id = id
        self.bonus_salary = bonus_salary

    def thuong_bophan_dict(self):
        return {self.id : self.bonus_salary}
# hàm trích xuất dữ liệu thuế
def trich_xuat_du_lieu_thue():
    import xml.etree.ElementTree as ET
    import urllib.request

    url_thue = "https://firebasestorage.googleapis.com/v0/b/funix-way.appspot.com/o/xSeries%2FChung%20chi%20dieu%20kien%2FPYB101x_1.1%2FASM_Resources%2Ftax.xml?alt=media&token=f7a6f73d-9e6d-4807-bb14-efc6875442c7"
    thue = urllib.request.urlopen(url_thue)
    data = thue.read().decode()

    tax_dict = {}
    tree = ET.fromstring(data)
    taxs = tree.findall('tax')

    # trả về kết quả dạng dict {(min,max) : value}
    for tax in taxs:
        min_val = int(tax.find('min').text)
        max_elem = tax.find('max')
        value = float(tax.find('value').text)

        if max_elem is not None:
            max_val = int(max_elem.text)
        else:
            # Giá trị mặc định cho max khi không tồn tại
            max_val = float('inf')
    # giá trị mặc định là x triệu đồng
        tax_range = [min_val * 1000000, max_val * 1000000]
        tax_dict[tuple(tax_range)] = value

    return tax_dict
# hàm trích xuất dữ liệu phạt đi muộn
def trich_xuat_du_lieu_phat():
    import urllib.request
    import json

    url = "https://firebasestorage.googleapis.com/v0/b/funix-way.appspot.com/o/xSeries%2FChung%20chi%20dieu%20kien%2FPYB101x_1.1%2FASM_Resources%2Flate_coming.json?alt=media&token=55246ee9-44fa-4642-aca2-dde101d705de"
    response = urllib.request.urlopen(url)
    data = response.read().decode('utf-8')
    json_data = json.loads(data)

    # trả về kết quả dạng dict {(min,max) : value}
    phat_dict = {}
    for item in json_data:
        min_val = int(item.get('min'))
        max_val = item.get('max', float('inf'))
        value = item.get('value')
        min_max = (min_val, max_val)
        phat_dict[min_max] = value

    return phat_dict
# hàm so sánh lương chưa thuế và tinh thuế
def calculate_income_tax(luong_chua_thue, tax_dict):
    for tax_range, tax_value in tax_dict.items():
        if tax_range[0] < luong_chua_thue <= tax_range[1]:
            return luong_chua_thue * tax_value / 100
    return 0
# hàm so sánh số ngày đi muộn và tính tiền phạt
def calculate_late(late_coming_day, phat_dict):
    for day, phat_value in phat_dict.items():
        if day[0] < late_coming_day <= day[1]:
            return late_coming_day * phat_value
    return 0
tax_dict = trich_xuat_du_lieu_thue()
phat_dict = trich_xuat_du_lieu_phat()


# Lưu dữ liệu nhân viên đúng class xuống file
def save_employee_data(employees, file):
    employee_data = []
    for employee in employees:
        employee_data.append({
            'id': employee.id,
            'name': employee.name,
            'salary_base': employee.salary_base,
            'working_days': employee.working_days,
            'department': employee.department,
            'working_performance': employee.working_performance,
            'bonus': employee.bonus,
            'late_coming_days': employee.late_coming_days,
            # lưu thêm tên class của nhân viên
            '__class__': employee.__class__.__name__  
        })

    with open(file, 'w') as f:
        json.dump(employee_data, f)

# Load lại dữ liệu nhân viên
def load_employee_data(file):
    with open(file, 'r') as f:
        employee_data = json.load(f)

    employees = []
    # lấy tên lớp của đối tượng nhân viên. Nếu không có trường '__class__' trong data, giá trị mặc định là 'Employee'
    for data in employee_data:
        class_name = data.pop('__class__', 'Employee')
        # truy cập class tương ứng thông qua tên class
        employee_class = globals()[class_name]
        # khởi tạo đối tượng nhân viên từ các thông tin trong data. **data cho phép truyền các thông số của data như các đối số đặt tên vào hàm khởi tạo của lớp nhân viên.
        employee = employee_class(**data)
        employees.append(employee)

    return employees


# lưu thông tin bộ phận xuống file
def save_department_data(departments, file):
    department_data = {}
    for department in departments:
        department_data[department.id] = department.bonus_salary

    with open(file, 'w') as f:
        json.dump(department_data, f)

# load lại dữ liệu bộ phận
def load_department_data(file):
    with open(file, 'r') as f:
        department_data = json.load(f)

    departments = []
    for id, bonus_salary in department_data.items():
        department = Department(id, bonus_salary)
        departments.append(department)

    return departments

employee_data_file = 'employee_data.json'
department_data_file = 'department_data.json'
# Đọc lại dữ liệu nhân viên và bộ phận từ tệp tin JSON, nếu file trống hoặc không có thì gán giá trị list rỗng
try:
    employees = list(load_employee_data(employee_data_file))
    departments = list(load_department_data(department_data_file))
except (FileNotFoundError, json.JSONDecodeError):
    employees = []
    departments = []

# chuyển list department thành dict để tiện tính toán 
departments_dict = {}
for department in departments:
    departments_dict[department.id] = department.bonus_salary

def in_dsnv(employees):
    for employee in employees:
        print("----")
        print("Mã số:", employee.id)
        print("Mã bộ phận:", employee.department)
        if isinstance(employee, Manager):
            print("Chức vụ: Quản lý")
        else:
            print("Chức vụ: Nhân viên")
        print("Họ và tên:", employee.name)
        print("Hệ số lương:", format(employee.salary_base, ",.2f"), "(VND)")
        print("Số ngày làm việc:", employee.working_days, "(ngày)")
        print("Hệ số hiệu quả:", employee.working_performance)
        print("Thưởng:", format(employee.bonus, ",.2f"), "(VND)")
        print("Số ngày đi muộn:", employee.late_coming_days)


def them_nhan_vien_moi():
    print("Thêm nhân viên mới ...")
    while True:
        ma_so = input("Nhập mã số: ")
        if ma_so == "":
            print("Bạn không được bỏ trống thông tin này")
        elif any(employee.id == ma_so for employee in employees):
            print("Mã nhân viên đã tồn tại")
        else:
            break

    while True:
        ma_bo_phan = input("Nhập mã bộ phận: ")
        if ma_bo_phan == "":
            print("Bạn không được bỏ trống thông tin này")
        elif not any(department.id == ma_bo_phan for department in departments):
            print("Mã bộ phận chưa tồn tại, tạo mới ...")
            thu_nhap_bo_phan = float(input("Nhập thưởng bộ phận: "))
            departments.append(Department(ma_bo_phan, thu_nhap_bo_phan))
            print("Đã tạo bộ phận mới ...")
        else:
            break

    while True:
        chuc_vu = input("Nhập chức vụ (NV / QL): ")
        if chuc_vu == "":
            print("Bạn không được bỏ trống thông tin này")
        elif chuc_vu not in ["NV", "QL"]:
            print("Chức vụ không hợp lệ")
        else:
            break

    while True:
        ho_ten = input("Nhập họ và tên: ")
        if ho_ten == "":
            print("Bạn không được bỏ trống thông tin này")
        else:
            break

    while True:
        try:
            he_so_luong = float(input("Nhập hệ số lương: "))
            if he_so_luong < 0:
                print("Bạn phải nhập một số không âm")
            else:
                break
        except ValueError:
            print("Bạn phải nhập một số")

    while True:
        try:
            so_ngay_lam_viec = int(input("Nhập số ngày làm việc: "))
            if so_ngay_lam_viec < 0:
                print("Bạn phải nhập một số không âm")
            else:
                break
        except ValueError:
            print("Bạn phải nhập một số")

    while True:
        try:
            he_so_hieu_qua = float(input("Nhập hệ số hiệu quả: "))
            if he_so_hieu_qua < 0:
                print("Bạn phải nhập một số không âm")
            else:
                break
        except ValueError:
            print("Bạn phải nhập một số")

    while True:
        try:
            thu_nhap_thuong = float(input("Nhập thưởng: "))
            if thu_nhap_thuong < 0:
                print("Bạn phải nhập một số không âm")
            else:
                break
        except ValueError:
            print("Bạn phải nhập một số")

    while True:
        try:
            so_ngay_di_muon = int(input("Nhập số ngày đi muộn: "))
            if so_ngay_di_muon < 0:
                print("Bạn phải nhập một số không âm")
            else:
                break
        except ValueError:
            print("Bạn phải nhập một số")

    # kiểm tra nếu chức vụ là ql hay nv thì nhân viên đó thuộc class tương ứng
    if chuc_vu == "QL":
        nhan_vien_moi = Manager(ma_so, ho_ten, he_so_luong, so_ngay_lam_viec, ma_bo_phan, he_so_hieu_qua, thu_nhap_thuong, so_ngay_di_muon)
        employees.append(nhan_vien_moi)
    else:
        nhan_vien_moi = Employee(ma_so, ho_ten, he_so_luong, so_ngay_lam_viec, ma_bo_phan, he_so_hieu_qua, thu_nhap_thuong, so_ngay_di_muon)
        employees.append(nhan_vien_moi)
    print("Đã thêm nhân viên mới ...")
    print("----")
    save_employee_data(employees, employee_data_file)

def xoa_nhan_vien():
    print("Xóa nhân viên theo ID")
    ma_nhan_vien = input("Nhập mã nhân viên muốn xóa: ")

    if ma_nhan_vien == "":
        print("Bạn không được bỏ trống thông tin này.")
        return

    found = False  # Biến đánh dấu tìm thấy nhân viên

    for employee in employees:
        if employee.id == ma_nhan_vien:
            employees.remove(employee)
            found = True
            print("Đã xóa thành công.")
            print("----")
            break

    if not found:
        print("Mã nhân viên không tồn tại.")
    save_employee_data(employees, employee_data_file)

def xoa_bo_phan():
    print("Xóa bộ phận theo ID")
    ma_bophan = input("Nhập mã bộ phận muốn xóa: ")

    if ma_bophan == "":
        print("Bạn không được bỏ trống thông tin này.")
        return

    found = False  # Biến đánh dấu tìm thấy bộ phận

    for department in departments:
        if department.id == ma_bophan:
            # Kiểm tra bộ phận có nhân viên hay không
            for employee in employees:
                if employee.department == ma_bophan:
                    print("Bạn không thể xóa bộ phận đang có nhân viên.")
                    return

            departments.remove(department)
            found = True
            print("Đã xóa thành công.")
            print("----")
            break

    if not found:
        print("Mã bộ phận không tồn tại.")
    save_department_data(departments, department_data_file)  

def hien_thi_bang_luong(employees, departments_dict):
    print("Bảng lương:")
    for employee in employees:
        print("----")
        print("Mã số:", employee.id)
        print("Lương sau thuế:", format(employee.calculate_salary(departments_dict, tax_dict, phat_dict), ",d"), "(VND)")


def doi_thongtin_nv():
    print("----")
    print("Chỉnh sửa thông tin nhân viên: ")
    while True:
        ma_so = input("Nhập mã số: ")
        if ma_so == "":
            print("Bạn không được bỏ trống thông tin này")
            continue
        # tạo biến trung gian found_employee rỗng, không trực tiếp sửa đổi thông tin nhân viên khi chưa hoàn thành nhập các thông tin
        found_employee = None
        for employee in employees:
            if ma_so == employee.id:
                found_employee = employee
                bophan = found_employee.department
                break
        if found_employee is None:
            print("Nhân viên không tồn tại")
            continue

        ten = input("Nhập họ và tên: ")
        if ten != "":
            found_employee.name = ten
        else:
            ten = found_employee.name

        chucvu = input("Nhập chức vụ (NV/QL): ")
        if chucvu != "" and chucvu not in ["NV", "QL"]:
            print("Bạn cần nhập đúng chức vụ: NV hoặc QL")
            continue

        # tạo các biến rỗng để kết hợp với lệnh try exept
        heso_luong = None
        ngay_lv = None
        heso_hieuqua = None
        thuong = None
        songay_muon = None

        heso_luong_input = input("Nhập hệ số lương: ")
        if heso_luong_input != "":
            try:
                heso_luong = float(heso_luong_input)
                if heso_luong < 0:
                    print("Bạn cần nhập một số dương")
                    continue
            except ValueError:
                print("Bạn cần nhập đúng định dạng số")
                continue
        else:
            heso_luong = found_employee.salary_base

        
        ngay_lv_input = input("Nhập số ngày làm việc: ")
        if ngay_lv_input != "":
            try:
                ngay_lv = int(ngay_lv_input)
                if ngay_lv < 0:
                    print("Bạn cần nhập một số dương")
                    continue
            except ValueError:
                print("Bạn cần nhập đúng định dạng số")
                continue
        else:
            ngay_lv = found_employee.working_days
        
        heso_hieuqua_input = input("Nhập hệ số hiệu quả: ")
        if heso_hieuqua_input != "":
            try:
                heso_hieuqua = float(heso_hieuqua_input)
                if heso_hieuqua < 0:
                    print("Bạn cần nhập một số dương")
                    continue
            except ValueError:
                print("Bạn cần nhập đúng định dạng số")
                continue
        else:
            heso_hieuqua = found_employee.working_performance

        
        thuong_input = input("Nhập thưởng: ")
        if thuong_input != "":
            try:
                thuong = int(thuong_input)
                if thuong < 0:
                    print("Bạn cần nhập một số dương")
                    continue
            except ValueError:
                print("Bạn cần nhập đúng định dạng số")
                continue
        else: 
            thuong = found_employee.bonus

        
        songay_muon_input = input("Nhập số ngày đi muộn: ")
        if songay_muon_input != "":
            try:
                songay_muon = int(songay_muon_input)
                if songay_muon < 0:
                    print("Bạn cần nhập một số dương")
                    continue
            except ValueError:
                print("Bạn cần nhập đúng định dạng số")
                continue
        else:
            songay_muon = found_employee.late_coming_days

        if chucvu == "NV":
            found_employee = Employee(ma_so, ten, heso_luong, ngay_lv, bophan, heso_hieuqua, thuong, songay_muon)
        elif chucvu == "QL":
            found_employee = Manager(ma_so, ten, heso_luong, ngay_lv, bophan, heso_hieuqua, thuong, songay_muon)

        # sau khi gán đầy đủ thuộc tính cho biến found_employee thì xoá nhân viên cũ đi và thêm lại nv đã sửa đổi
        employees.remove(employee)
        employee = found_employee
        employees.append(employee)

        save_employee_data(employees, employee_data_file)
        print("Đã hoàn tất chỉnh sửa")
        print("----")
        print("Mã số:", employee.id)
        print("Mã bộ phận:", employee.department)
        if isinstance(employee, Manager):
            print("Chức vụ: Quản lý")
        else:
            print("Chức vụ: Nhân viên")
        print("Họ và tên:", employee.name)
        print("Hệ số lương:", employee.salary_base, "(VND)")
        print("Số ngày làm việc:", employee.working_days, "(ngày)")
        print("Hệ số hiệu quả:", employee.working_performance)
        print("Thưởng:", format(employee.bonus, ",.2f"), "(VND)")
        print("Số ngày đi muộn:", employee.late_coming_days)
        break










                
        



    # Hiển thị chương trình
while True:
    print('''
    MENU QUẢN LÝ NHÂN VIÊN
    1. Hiển thị danh sách nhân viên
    2. Hiển thị danh sách bộ phận
    3. Thêm nhân viên mới
    4. Xoá nhân viên theo ID
    5. Xoá bộ phận theo ID
    6. Hiển thị bảng lương
    7. Thay đổi thông tin nhân viên
    8. Thoát
    ''')
    a = input('Mời bạn chọn chức năng mong muốn: ')
    if a.isdigit():
        a = int(a)
        if a == 1:
            if len(employees) == 0:
                print('Hiện chưa có nhân viên.')
            else: 
                print(in_dsnv(employees))
        elif a == 2:
            if len(departments) == 0:
                print('Hiện chưa có bộ phận.')
            else: 
                for department in departments:
                    print('----')
                    print('Mã bộ phận: ', department.id)
                    print('Mức thưởng: ', format(department.bonus_salary, ",.2f"), "(VND)")
        elif a == 3:
            them_nhan_vien_moi()
        elif a == 4:
            xoa_nhan_vien()
        elif a == 5:
            xoa_bo_phan()
        elif a == 6:
            hien_thi_bang_luong(employees, departments_dict)
        elif a ==7:
            doi_thongtin_nv()
        elif a == 8:
            exit()


