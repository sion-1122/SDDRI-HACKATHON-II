/* Register page (server component).

[Task]: T031, T075
[From]: specs/001-user-auth/plan.md, specs/005-ux-improvement/tasks.md

Updated with Notion-inspired minimalistic design using theme variables.
*/
import { RegisterForm } from "@/components/auth/RegisterForm";

export const metadata = {
  title: "Create Account - Todo List",
  description: "Create a new Todo List account",
};

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-[95vw] sm:max-w-lg md:max-w-xl lg:max-w-2xl">
        {/* Notion-inspired header - clean and minimal */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-semibold text-foreground tracking-tight mb-2">
            Create your account
          </h1>
          <p className="text-sm text-muted-foreground">
            Or{" "}
            <a
              href="/login"
              className="font-medium text-foreground hover:text-primary transition-colors underline-offset-4 hover:underline"
            >
              sign in to existing account
            </a>
          </p>
        </div>
        <RegisterForm />
      </div>
    </div>
  );
}