function sysCall_init()
    corout=coroutine.create(coroutineMain)
end

function sysCall_actuation()
    if coroutine.status(corout)~='dead' then
        local ok,errorMsg=coroutine.resume(corout)
        if errorMsg then
            error(debug.traceback(corout,errorMsg),2)
        end
    end
end

function append_list_moviments(id)
    move_to_execute[#move_to_execute+1]=id
end

function execute_moviment(intData,floatData,stringData,buffer)
    move_to_execute[#move_to_execute+1]=buffer
    return {},{},{},''
end

function moveData(movData)
    all_data_move[movData.id]=movData
end

function data_to_moviment(intData,floatData,stringData,buffer)
    if not messagePack then
        messagePack=require('messagePack')
        messagePack.set_string('string')
    end
    local movData=messagePack.unpack(buffer)
    all_data_move[movData.id]=movData
    return {},{},{},''
end

function is_moving()
    for i = 1, 6 do
        local wheelVelocity = sim.getJointVelocity(wheels[i])
        if math.abs(wheelVelocity) >= 0.1 then
            return true
        end
    end
    return false
end

function stop_move()
    for i = 1,6 do
        sim.setJointTargetVelocity(wheels[i], 0.0)
    end
end

function arm_move(id, arm, angle)
    stop_move()
    while is_moving() do
        sim.wait(0.5)
        stop_move()
    end
    sim.setJointTargetPosition(arm[id], math.rad(angle))
    local angleCurrent = math.rad(tonumber(string.format("%.2f", math.abs(sim.getJointPosition(arm[id])))))
    local angleTarget = math.rad(tonumber(string.format("%.2f", math.abs(angle))))
    local dif = tonumber(string.format("%.2f", math.abs(angleTarget) - math.abs(angleCurrent)))
    while ((dif > 0.01) and (angleCurrent ~= angleTarget)) do
        sim.wait(0.5)
        dif = math.rad(tonumber(string.format("%.2f", math.abs(angleTarget) - math.abs(angleCurrent))))
        angleCurrent = tonumber(string.format("%.2f", math.abs(sim.getJointPosition(arm[id]))))
    end
end

function coroutineMain()
    signal_name='base_link_Executado'
    move_to_execute={}
    all_data_move={}
	
	--- Wheels config:
    wheels={
		sim.getObjectHandle('wheel_front_right'),
		sim.getObjectHandle('wheel_front_left'),
		sim.getObjectHandle('wheel_middle_right'),
		sim.getObjectHandle('wheel_middle_left'),
		sim.getObjectHandle('wheel_back_right'),
		sim.getObjectHandle('wheel_back_left')
	}

	--- Brackets config:
	bracket={
		sim.getObjectHandle('angle_bracket_front_right'),
		sim.getObjectHandle('angle_bracket_front_left'),
		sim.getObjectHandle('angle_bracket_back_right'),
		sim.getObjectHandle('angle_bracket_back_left')
	}
    --- Pantilt config:
	rotation_pantilt = sim.getObjectHandle('rotation_pantilt')
    incline_pantilt = sim.getObjectHandle('incline_pantilt')
    
	--- Arms config:
	arm={
		sim.getObjectHandle('rotation_arm'),
		sim.getObjectHandle('incline_arm_ext1'),
		sim.getObjectHandle('incline_arm_ext2'),
		sim.getObjectHandle('rightGripper'),
		sim.getObjectHandle('leftGripper')
	}
	-------------  Iniciando objetos com velocidade zero: -------
    for i = 1,6 do
        sim.setJointTargetVelocity(wheels[i], 0.0)
    end
    for i = 1, 4 do
        sim.setJointTargetPosition(bracket[i], 0.0)
    end
    sim.setJointTargetPosition(rotation_pantilt, 0.0)
    sim.setJointTargetPosition(incline_pantilt, math.rad(90.0))
    --- Arm:
    sim.setJointTargetPosition(arm[1], math.rad(90.0))
    sim.setJointTargetPosition(arm[2], math.rad(-30.0))
    sim.setJointTargetPosition(arm[3], math.rad(0.0))
    sim.setJointTargetVelocity(arm[4], math.rad(90.0))
    sim.setJointTargetVelocity(arm[5], math.rad(90.0))
    -------------------------------------------------------------
	sim.setStringSignal(signal_name,'signal_rover')
    while true do
        if #move_to_execute>0 then
            local id=table.remove(move_to_execute,1)
            local moveData=all_data_move[id]
            all_data_move[id]=nil
            sim.setStringSignal(signal_name,id)
            if moveData.type == 'move' then
                 -- Mantem brackets nas posicoes atuais
                for i = 1, 4 do
                    sim.setJointTargetPosition(bracket[i], sim.getJointPosition(bracket[i]))
                end
                for i = 1,6 do
                    sim.setJointTargetVelocity(wheels[i], moveData.Data[i]*math.pi/180)
                end
            end
            if moveData.type == 'stop_move' then
                for i = 1, 4 do
                    sim.setJointTargetPosition(bracket[i], sim.getJointPosition(bracket[i]))
                end
                for i = 1,6 do
                    sim.setJointTargetVelocity(wheels[i], 0.0)
                end
            end
            if moveData.type == 'turn' then
                while is_moving() do
                    stop_move()
                    sim.wait(1)
                end
                for i = 1, 4 do
                    sim.setJointTargetPosition(bracket[i], math.rad(moveData.Data[i]))
                end
         	end
            if moveData.type == 'rotation_pantilt' then
                sim.setJointTargetPosition(rotation_pantilt, math.rad(moveData.Data))
         	end
            if moveData.type == 'incline_pantilt' then
                sim.setJointTargetPosition(incline_pantilt, math.rad(moveData.Data))
         	end
			if moveData.type == 'rotation_arm' then
                arm_move(1, arm, moveData.Data)
         	end
            if moveData.type == 'incline_ext1' then
                arm_move(2, arm, moveData.Data)
         	end
            if moveData.type == 'incline_ext2' then
                arm_move(3, arm, moveData.Data)
         	end
            if moveData.type == 'gripper' then
                stop_move()
                sim.setJointTargetPosition(arm[4], math.rad(moveData.Data))
                sim.setJointTargetPosition(arm[5], math.rad(moveData.Data)) 
         	end
            
            
        end  
    end
end