import UploadForm from "@/components/UploadForm";

export default function UploadPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Upload Game</h1>
      <p className="text-gray-400 text-sm">
        Upload your PyGame as a ZIP file. The ZIP should contain the game source
        code with a main entry point. Optionally include a config.yaml.
      </p>
      <UploadForm />
    </div>
  );
}
