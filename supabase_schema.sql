-- Create a table for public profiles using Supabase Auth
create table profiles (
  id uuid references auth.users not null primary key,
  email text,
  role text default 'user',
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable Row Level Security (RLS)
alter table profiles enable row level security;

create policy "Public profiles are viewable by everyone."
  on profiles for select
  using ( true );

create policy "Users can insert their own profile."
  on profiles for insert
  with check ( auth.uid() = id );

create policy "Users can update own profile."
  on profiles for update
  using ( auth.uid() = id );

-- Handle new user signup automatically
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, email, role)
  values (new.id, new.email, 'user');
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- Table for tracking votes
create table distro_votes (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users not null,
  distro_name text not null,
  vote_type integer not null check (vote_type in (1, -1)),
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  unique(user_id, distro_name)
);

alter table distro_votes enable row level security;

create policy "Votes are viewable by everyone"
  on distro_votes for select
  using ( true );

create policy "Authenticated users can vote"
  on distro_votes for insert
  with check ( auth.role() = 'authenticated' );

create policy "Users can update their own votes"
  on distro_votes for update
  using ( auth.uid() = user_id );

-- Table for proposing edits
create table distro_edits (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users not null,
  distro_name text not null,
  field text not null,
  new_value text not null,
  status text default 'pending' check (status in ('pending', 'approved', 'rejected')),
  admin_comment text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table distro_edits enable row level security;

create policy "Edits are viewable by everyone"
  on distro_edits for select
  using ( true );

create policy "Authenticated users can propose edits"
  on distro_edits for insert
  with check ( auth.role() = 'authenticated' );

create policy "Users can see their own edits"
  on distro_edits for update
  using ( auth.uid() = user_id );

-- Only admins can update status (This needs to be enforced via App logic or separate Admin role policy)
-- For now, we allow update if user is same (for basic edit) or if we implement admin RLS later.
