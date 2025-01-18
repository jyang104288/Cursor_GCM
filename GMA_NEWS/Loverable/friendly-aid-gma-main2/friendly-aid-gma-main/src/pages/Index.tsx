// Start Backend Server:
// cd C:\Users\104288\.cursor-tutor\Cursor_GCM\GMA_NEWS\Backend
// python GMA_Backend.py
//
// Start Frontend Server:
// 1. Open your Terminal App
// 2. cd C:\Users\104288\.cursor-tutor\Cursor_GCM\GMA_NEWS\Loverable\friendly-aid-gma-main2\friendly-aid-gma-main
// npm run dev




import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Save } from "lucide-react";
import { saveAs } from 'file-saver';
import * as XLSX from 'xlsx';
import { Progress } from "@/components/ui/progress";

const attributes = [
  "Title", "Summary", "Affected Products", "Summary Details", 
  "Conformity Assessment", "Marking Requirement", "Technical Requirement",
  "Publish Date", "Effective Date", "Mandatory Date", "Consultation Closing"
];

export default function Index() {
  const [topic, setTopic] = useState("");
  const [url, setUrl] = useState("");
  const [analysisResults, setAnalysisResults] = useState({});
  const [expertAnalysis, setExpertAnalysis] = useState({});
  const [feedback, setFeedback] = useState({});
  const [accuracy, setAccuracy] = useState({});
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async () => {
    console.log("Submit button clicked");
    console.log("Topic:", topic);
    console.log("URL:", url);

    if (!topic || !url) {
      toast({
        title: "Validation Error",
        description: "Please enter both topic and URL",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    toast({
      title: "Processing",
      description: "Analyzing content...",
    });

    try {
      const response = await fetch("http://127.0.0.1:5000/process", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ topic, url }),
      });

      console.log("Response status:", response.status);

      if (!response.ok) {
        const errorData = await response.json();
        if (errorData.error.includes("not validated")) {
          throw new Error(
            "The entered domain is not supported. Supported domains include:\n" +
            "CEN-CENELEC\n" +
            "IEC Webstore\n" +
            "Standards Council of Canada\n" +
            "European Commission\n" +
            "IECEE\n" +
            "EUR-Lex\n" +
            "GCC Standardization Organization\n" +
            "Vietnam Ministry of Information and Communications\n" +
            "China Quality Certification Centre\n" +
            "Korean Agency for Technology and Standards\n" +
            "Brazilian Government Portal\n" +
            "Standards Australia\n" +
            "Turkish Official Gazette\n" +
            "Saudi National Portal for Government Services\n" +
            "Brazilian Government Portal"
          );
        }
        throw new Error(errorData.error || "Network response was not ok");
      }

      const data = await response.json();
      console.log("Analysis Results:", data);
      setAnalysisResults(data);
    } catch (error) {
      console.error("Error during fetch:", error);
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    console.log("Clearing input fields");
    setTopic("");
    setUrl("");
    setAnalysisResults({});
  };

  const handleSave = () => {
    const fileName = prompt("Please enter the file name:", "analysis_results.xlsx");
    if (!fileName) {
      toast({
        title: "Error",
        description: "File name is required.",
        variant: "destructive",
      });
      return; // Exit if no file name is provided
    }

    // Prepare data for the Excel file
    const data = attributes.map(attr => ({
      Attribute: attr,
      Prompt: analysisResults[attr]?.prompt || '',
      AI_Output: analysisResults[attr]?.ai_output || '',
      Expert_Analysis: expertAnalysis[attr] || '',
      Feedback: feedback[attr] || '',
      Accuracy: accuracy[attr] || '',
    }));

    console.log("Data prepared for Excel:", data);

    // Create a new workbook and a worksheet
    const worksheet = XLSX.utils.json_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Analysis Results');

    // Generate buffer and save the file
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([excelBuffer], { type: 'application/octet-stream' });
    saveAs(blob, fileName); // Save the file with the user-defined name

    toast({
      title: "Success",
      description: `Analysis results saved successfully as ${fileName}.`,
    });
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold tracking-tight mb-2 text-red-600">
          AI Assisted Research Tool
        </h1>
        <div className="flex justify-start mb-4">
          <div className="bg-gray-50 border border-gray-300 rounded-lg p-4 shadow-md w-full">
            <p className="font-bold text-lg text-left text-gray-800">
              This tool currently supports analysis for the following domains:
            </p>
            <ul className="list-disc list-inside text-left text-sm text-gray-700">
              <li>CEN-CENELEC</li>
              <li>IEC Webstore</li>
              <li>Standards Council of Canada</li>
              <li>European Commission</li>
              <li>IECEE</li>
              <li>EUR-Lex</li>
              <li>GCC Standardization Organization</li>
              <li>Vietnam Ministry of Information and Communications</li>
              <li>China Quality Certification Centre</li>
              <li>Korean Agency for Technology and Standards</li>
              <li>Brazilian Government Portal</li>
              <li>Standards Australia</li>
              <li>Turkish Official Gazette</li>
              <li>Saudi National Portal for Government Services</li>
              <li>Brazilian Government Portal</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Input Section */}
      <Card className="glass-card mb-8">
        <CardHeader>
          <CardTitle className="text-lg text-gray-800">Research Parameters</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Topic</label>
              <Input
                placeholder="Enter research topic"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="input-field border-gray-300"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">URL</label>
              <Input
                placeholder="Enter URL to analyze"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="input-field border-gray-300"
              />
            </div>
          </div>
          
          <div className="flex justify-end space-x-2">
            <Button
              variant="outline"
              onClick={handleClear}
              className="button-hover bg-red-600 text-white hover:bg-red-700"
            >
              Clear
            </Button>
            <Button 
              onClick={handleSubmit}
              className="button-hover bg-red-600 text-white hover:bg-red-700"
            >
              Analyze
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Results Section */}
      <Card className="glass-card mb-8">
        <CardHeader>
          <CardTitle className="text-lg text-gray-800">Analysis Results</CardTitle>
        </CardHeader>
        <CardContent>
          {loading && <Progress value={100} />}
          <Tabs defaultValue={attributes[0]} className="w-full">
            <ScrollArea className="w-full mb-4">
              <TabsList className="w-full inline-flex flex-wrap justify-start gap-2 h-auto p-2">
                {attributes.map((attr) => (
                  <TabsTrigger
                    key={attr}
                    value={attr}
                    className="whitespace-nowrap"
                  >
                    {attr}
                  </TabsTrigger>
                ))}
              </TabsList>
            </ScrollArea>

            {attributes.map((attr) => (
              <TabsContent key={attr} value={attr} className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg text-gray-800">{attr} Analysis</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-700">LLM Prompt</label>
                      <Textarea
                        placeholder="AI prompt will appear here"
                        className="h-24 input-field bg-muted/50 border-gray-300"
                        readOnly
                        value={analysisResults[attr]?.prompt || ""}
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-700">AI Generated Analysis</label>
                      <Textarea
                        placeholder="AI analysis will appear here"
                        className="h-32 input-field border-gray-300"
                        value={analysisResults[attr]?.ai_output || ""}
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-700">Expert Analysis for {attr}</label>
                      <Textarea
                        placeholder="Enter expert analysis"
                        value={expertAnalysis[attr] || ''}
                        onChange={(e) => setExpertAnalysis({ ...expertAnalysis, [attr]: e.target.value })}
                        className="h-32 input-field border-gray-300"
                      />
                      <label className="text-sm font-medium text-gray-700">Feedback</label>
                      <Input
                        placeholder="Enter feedback"
                        value={feedback[attr] || ''}
                        onChange={(e) => setFeedback({ ...feedback, [attr]: e.target.value })}
                        className="input-field border-gray-300"
                      />
                      <label className="text-sm font-medium text-gray-700">Accuracy (%)</label>
                      <Input
                        type="number"
                        min="0"
                        max="100"
                        placeholder="Enter accuracy"
                        value={accuracy[attr] || ''}
                        onChange={(e) => setAccuracy({ ...accuracy, [attr]: e.target.value })}
                        className="input-field border-gray-300"
                      />
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button
          onClick={handleSave}
          className="button-hover bg-red-600 text-white hover:bg-red-700"
          variant="default"
        >
          <Save className="mr-2" />
          Save Results
        </Button>
      </div>
    </div>
  );
}