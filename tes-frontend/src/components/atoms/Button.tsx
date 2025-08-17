/*
================================================================================
File: frontend/src/components/atoms/Button.tsx
Purpose: A refined, reusable button component. We've updated the styling
         to use our vibrant magenta/fuchsia accent color.
================================================================================
*/
import React from 'react';

type ButtonProps = {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
  className?: string;
} & React.ButtonHTMLAttributes<HTMLButtonElement>;

const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  className = '',
  ...props
}) => {
  const baseStyle = `
    font-bold py-2 px-4 rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900
    transition-all duration-200 ease-in-out transform hover:scale-105
    disabled:opacity-50 disabled:cursor-not-allowed disabled:scale-100
  `;

  const variantStyles = {
    primary: 'bg-fuchsia-600 hover:bg-fuchsia-500 text-white focus:ring-fuchsia-500',
    secondary: 'bg-slate-700 hover:bg-slate-600 text-slate-200 focus:ring-slate-500',
  };

  const combinedClassName = `${baseStyle} ${variantStyles[variant]} ${className}`;

  return (
    <button className={combinedClassName} onClick={onClick} {...props}>
      {children}
    </button>
  );
};

export default Button;
