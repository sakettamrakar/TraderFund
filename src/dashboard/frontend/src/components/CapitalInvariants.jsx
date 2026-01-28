import React from 'react';
import './CapitalInvariants.css';

const CapitalInvariants = () => {
    return (
        <div className="capital-invariants">
            <h4 className="inv-title">🔒 System Invariants</h4>
            <ul className="inv-list">
                <li>No capital without explicit authorization</li>
                <li>No leverage (Strict 1.0x Cap)</li>
                <li>No execution paths (Observer Only)</li>
                <li>All limits enforced before action</li>
            </ul>
        </div>
    );
};

export default CapitalInvariants;
