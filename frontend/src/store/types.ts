export interface RootState {
    loggedIn: boolean;
    userDetails: UserDetails | null;
    userId: string | null;
  }
  
  export interface UserDetails {
    id: string;
    username: string;
  }