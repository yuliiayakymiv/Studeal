import Footer from "@/components/Footer";
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "react-oidc-context";
import Header from "@/components/Header";
import Home from "@/pages/Home";
import Catalog from "@/pages/Catalog";
import DealPage from "@/pages/DealPage";
import Events from "@/pages/Events";
import Saved from "@/pages/Saved";
import Subscription from "@/pages/Subscription";

// Незалогіненим показуємо головну і нічого не вантажимо.
function RequireAuth({ children }) {
  const auth = useAuth();
  if (auth.isLoading) return <p className="p-8 text-muted-foreground">Завантаження…</p>;
  if (!auth.isAuthenticated) return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  return (
    <div className="flex min-h-screen flex-col bg-muted/30">
      <Header />
      <main className="mx-auto w-full max-w-5xl flex-1 p-4">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/catalog" element={<RequireAuth><Catalog /></RequireAuth>} />
          <Route path="/deals/:id" element={<RequireAuth><DealPage /></RequireAuth>} />
          <Route path="/events" element={<RequireAuth><Events /></RequireAuth>} />
          <Route path="/saved" element={<RequireAuth><Saved /></RequireAuth>} />
          <Route path="/subscription" element={<RequireAuth><Subscription /></RequireAuth>} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}
