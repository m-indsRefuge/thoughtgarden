// ==============================================================================
// 3. FIXED ExperimentForm.tsx
// ==============================================================================

import React, { useState } from "react";

interface ExperimentData {
  title: string;
  description: string;
}

interface ExperimentFormProps {
  onSubmit?: (data: ExperimentData) => void;
  onCancel?: () => void;
  initialData?: Partial<ExperimentData>;
  isLoading?: boolean;
}

const ExperimentForm: React.FC<ExperimentFormProps> = ({
  onSubmit,
  onCancel,
  initialData,
  isLoading = false
}) => {
  const [title, setTitle] = useState(initialData?.title || "");
  const [description, setDescription] = useState(initialData?.description || "");
  const [errors, setErrors] = useState<Partial<ExperimentData>>({});

  const validateForm = (): boolean => {
    const newErrors: Partial<ExperimentData> = {};
    
    if (!title.trim()) {
      newErrors.title = "Title is required";
    } else if (title.trim().length < 3) {
      newErrors.title = "Title must be at least 3 characters";
    }
    
    if (!description.trim()) {
      newErrors.description = "Description is required";
    } else if (description.trim().length < 10) {
      newErrors.description = "Description must be at least 10 characters";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    const experimentData: ExperimentData = {
      title: title.trim(),
      description: description.trim()
    };
    
    console.log("Submitting experiment:", experimentData);
    
    if (onSubmit) {
      onSubmit(experimentData);
    }
  };

  const handleReset = () => {
    setTitle(initialData?.title || "");
    setDescription(initialData?.description || "");
    setErrors({});
  };

  return (
    <div className="bg-white bg-opacity-90 p-6 rounded-lg shadow-md max-w-md w-full mx-auto">
      <h3 className="text-xl font-bold mb-4 text-gray-800">
        Create Thought Experiment
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
            Experiment Title *
          </label>
          <input
            id="title"
            type="text"
            placeholder="Enter a thought-provoking title..."
            value={title}
            onChange={(e) => {
              setTitle(e.target.value);
              if (errors.title) {
                setErrors(prev => ({ ...prev, title: undefined }));
              }
            }}
            className={`border rounded-md p-3 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.title ? 'border-red-500' : 'border-gray-300'
            }`}
            disabled={isLoading}
          />
          {errors.title && (
            <p className="text-red-500 text-sm mt-1">{errors.title}</p>
          )}
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            Description *
          </label>
          <textarea
            id="description"
            placeholder="Describe your thought experiment in detail..."
            value={description}
            onChange={(e) => {
              setDescription(e.target.value);
              if (errors.description) {
                setErrors(prev => ({ ...prev, description: undefined }));
              }
            }}
            className={`border rounded-md p-3 w-full h-32 resize-vertical focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.description ? 'border-red-500' : 'border-gray-300'
            }`}
            disabled={isLoading}
          />
          {errors.description && (
            <p className="text-red-500 text-sm mt-1">{errors.description}</p>
          )}
        </div>

        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={isLoading}
            className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex-1"
          >
            {isLoading ? "Creating..." : "Create Experiment"}
          </button>
          
          <button
            type="button"
            onClick={handleReset}
            disabled={isLoading}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 disabled:opacity-50"
          >
            Reset
          </button>
          
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              disabled={isLoading}
              className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 disabled:opacity-50"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
      
      <div className="mt-4 text-xs text-gray-500">
        * Required fields
      </div>
    </div>
  );
};

export default ExperimentForm;