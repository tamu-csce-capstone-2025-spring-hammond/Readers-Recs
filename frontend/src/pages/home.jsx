import React from 'react';
import Navbar from '../components/navbar';
import "../style/style.css";

const Home = () => {
    return (
    <div>
        {/* Top Section (Book Recommendations) */}
        <div className='book-recommendation-view'>
            <h1>Book RECOMMENDATIONS</h1>
            <div className='book-recommendation-covers'>
                {/* Spots for 5 Book Covers Recommended GO HERE */}
                <div></div>
                <div></div>
                <div></div>
                <div></div>
                <div></div>
            </div>
        </div>
        {/* Bottom Section (Current Read, Last Finished, To-Read) */}
        <div className='home-bottom-section'>
            {/* Current Read */}
            <div className='current-read-view'>
                <h1>Current Read</h1>
                <div className='current-read-cover'></div>
                <button className='text-button'>Update Progress</button>
            </div>
            {/* Last Finished */}
            <div className='last-finished-view'>
                <h1>Last Finished</h1>
                <div className='last-finished-cover'></div>
                <button className='text-button'>Go to Chat→</button>
            </div>
            {/* To-Read Shelf*/}
            <div className='to-read-view'>
                <h1>To-Read Shelf</h1>
                <div className='to-read-scroll-area'>
                    {/* Vector/List of To-Read Covers GO HERE */}
                </div>
                <button className='round-button'>→</button>
            </div>
        </div>
        <Navbar /> {}
    </div>
    );
};

export default Home;