import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "CampusAid",
  description: "University complaint system portal"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning className="min-h-screen">
        {children}
      </body>
    </html>
  );
}
