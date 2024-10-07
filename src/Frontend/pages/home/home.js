import React from "react"
import { Helmet } from 'react-helmet'
import Icon from "../../templates/icon";

class Home extends React.Component {
    render() {
        return(
            <>
                <Helmet>
                    <title>{ 'Home - Stack Overflow' }</title>
                </Helmet>
                <Icon />
                <p>This is Home</p>
            </>
        );
    }
} 

export default Home;