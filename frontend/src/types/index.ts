export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_superuser: boolean;
}

export interface TeacherProfile {
  phone: string;
  profile_picture: string;
  lecture_hall?: LectureHall;
}

export interface LectureHall {
  id: number;
  hall_name: string;
  building: string;
  assigned_teacher?: User;
}

export interface MalpracticeLog {
  id: number;
  date: string;
  time: string;
  malpractice: string;
  proof: string;
  lecture_hall: LectureHall;
  verified: boolean;
  is_malpractice: boolean;
}

export interface AuthContextType {
  user: User | null;
  profile: TeacherProfile | null;
  isLoading: boolean;
  isAdmin: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  updateProfile: (data: Partial<User & TeacherProfile>) => Promise<void>;
  changePassword: (oldPassword: string, newPassword: string) => Promise<void>;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone: string;
  profile_picture?: File;
}
